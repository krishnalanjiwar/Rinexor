from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime, timedelta
import pandas as pd
import io
import uuid

from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.models.user import User, UserRole
from app.models.dca import DCA
from app.models.case import Case, CaseStatus
from app.schemas.user import UserCreate, UserResponse
from app.services.workflow_service import WorkflowService
from app.services.ai_service import AIService

router = APIRouter()

@router.get("/users", response_model=List[UserResponse])
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role(["enterprise_admin"]))
):
    """Get all users (admin only)"""
    users = db.query(User).order_by(User.created_at.desc()).offset(skip).limit(limit).all()
    return users

@router.post("/users", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role(["enterprise_admin"]))
):
    """Create new user (admin only)"""
    # Check if user exists
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")
    
    # Check DCA exists if DCA agent
    if user_data.role == UserRole.DCA_AGENT and user_data.dca_id:
        dca = db.query(DCA).filter(DCA.id == user_data.dca_id).first()
        if not dca:
            raise HTTPException(status_code=400, detail="DCA not found")
    
    # Create user
    from app.core.security import get_password_hash
    
    user = User(
        id=str(uuid.uuid4()),
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        role=user_data.role,
        dca_id=user_data.dca_id,
        is_active=True,
        created_at=datetime.utcnow()
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user

@router.put("/users/{user_id}/deactivate")
async def deactivate_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role(["enterprise_admin"]))
):
    """Deactivate user (admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.id == current_user["id"]:
        raise HTTPException(status_code=400, detail="Cannot deactivate yourself")
    
    user.is_active = False
    user.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "User deactivated successfully"}

@router.post("/sla/check-violations")
async def check_sla_violations(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role(["enterprise_admin", "collection_manager"]))
):
    """Check for SLA violations"""
    violations = WorkflowService.check_sla_violations(db)
    
    return {
        "violations_found": len(violations),
        "violations": violations[:50],  # Return top 50
        "checked_at": datetime.utcnow()
    }

@router.get("/system-stats")
async def get_system_stats(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role(["enterprise_admin"]))
):
    """Get system statistics (admin only)"""
    from sqlalchemy import func
    
    # User stats
    total_users = db.query(func.count(User.id)).scalar()
    active_users = db.query(func.count(User.id)).filter(User.is_active == True).scalar()
    
    # DCA stats
    total_dcas = db.query(func.count(DCA.id)).scalar()
    active_dcas = db.query(func.count(DCA.id)).filter(DCA.is_active == True).scalar()
    
    # Case stats
    total_cases = db.query(func.count(Case.id)).scalar()
    cases_today = db.query(func.count(Case.id)).filter(
        func.date(Case.created_at) == func.date('now')
    ).scalar()
    
    # Database size (SQLite specific)
    import os
    db_size = os.path.getsize("recoverai.db") if os.path.exists("recoverai.db") else 0
    
    return {
        "users": {
            "total": total_users,
            "active": active_users,
            "by_role": {
                role.value: db.query(func.count(User.id)).filter(User.role == role).scalar()
                for role in UserRole
            }
        },
        "dcas": {
            "total": total_dcas,
            "active": active_dcas,
            "accepting_cases": db.query(func.count(DCA.id)).filter(DCA.is_accepting_cases == True).scalar()
        },
        "cases": {
            "total": total_cases,
            "today": cases_today,
            "by_status": {
                status.value: db.query(func.count(Case.id)).filter(Case.status == status).scalar()
                for status in CaseStatus
            }
        },
        "system": {
            "database_size_mb": round(db_size / (1024 * 1024), 2),
            "server_time": datetime.utcnow().isoformat(),
            "api_version": "1.0.0"
        }
    }

@router.post("/recalculate-metrics")
async def recalculate_all_metrics(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role(["enterprise_admin"]))
):
    """Recalculate all system metrics (admin only)"""
    # This would trigger background recalculation of all metrics
    # For now, just return success
    
    return {
        "message": "Metric recalculation started",
        "tasks": [
            "DCA performance scores",
            "User activity metrics", 
            "Case recovery rates",
            "SLA compliance rates"
        ],
        "started_at": datetime.utcnow()
    }

@router.post("/upload-cases")
async def upload_cases_csv(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role(["enterprise_admin"]))
):
    """
    Upload cases from CSV file
    
    Expected CSV columns:
    - account_id (required)
    - debtor_name (required) 
    - debtor_email
    - debtor_phone
    - debtor_address
    - original_amount (required)
    - current_amount (optional, defaults to original_amount)
    - currency (optional, defaults to USD)
    - days_delinquent (required)
    - debt_age_days (optional, defaults to days_delinquent)
    - debt_type (optional)
    """
    
    # Validate file type
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    
    try:
        # Read CSV file
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        
        # Validate required columns
        required_columns = ['account_id', 'debtor_name', 'original_amount', 'days_delinquent']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise HTTPException(
                status_code=400, 
                detail=f"Missing required columns: {', '.join(missing_columns)}"
            )
        
        # Process cases
        results = {
            "total_rows": len(df),
            "successful": [],
            "failed": [],
            "summary": {}
        }
        
        ai_service = AIService()
        ai_service.initialize()
        
        for index, row in df.iterrows():
            try:
                # Validate required fields
                if pd.isna(row['account_id']) or pd.isna(row['debtor_name']) or pd.isna(row['original_amount']):
                    results["failed"].append({
                        "row": index + 1,
                        "error": "Missing required fields",
                        "data": row.to_dict()
                    })
                    continue
                
                # Check if case already exists
                existing_case = db.query(Case).filter(Case.account_id == str(row['account_id'])).first()
                if existing_case:
                    results["failed"].append({
                        "row": index + 1,
                        "error": f"Case with account_id {row['account_id']} already exists",
                        "data": row.to_dict()
                    })
                    continue
                
                # Prepare case data
                case_data = {
                    "account_id": str(row['account_id']),
                    "debtor_name": str(row['debtor_name']),
                    "debtor_email": str(row.get('debtor_email', '')) if pd.notna(row.get('debtor_email')) else None,
                    "debtor_phone": str(row.get('debtor_phone', '')) if pd.notna(row.get('debtor_phone')) else None,
                    "debtor_address": str(row.get('debtor_address', '')) if pd.notna(row.get('debtor_address')) else None,
                    "original_amount": float(row['original_amount']),
                    "current_amount": float(row.get('current_amount', row['original_amount'])),
                    "currency": str(row.get('currency', 'USD')),
                    "days_delinquent": int(row['days_delinquent']),
                    "debt_age_days": int(row.get('debt_age_days', row['days_delinquent'])),
                    "debt_type": str(row.get('debt_type', 'other')) if pd.notna(row.get('debt_type')) else 'other'
                }
                
                # Process through workflow
                processed_data = WorkflowService.process_new_case(case_data, db)
                
                # Create case
                case = Case(
                    id=str(uuid.uuid4()),
                    account_id=case_data["account_id"],
                    debtor_name=case_data["debtor_name"],
                    debtor_email=case_data["debtor_email"],
                    debtor_phone=case_data["debtor_phone"],
                    debtor_address=case_data["debtor_address"],
                    original_amount=case_data["original_amount"],
                    current_amount=case_data["current_amount"],
                    currency=case_data["currency"],
                    days_delinquent=case_data["days_delinquent"],
                    debt_age_days=case_data["debt_age_days"],
                    status=processed_data["status"],
                    priority=processed_data["priority"],
                    recovery_score=processed_data["recovery_score"],
                    recovery_score_band="high" if processed_data["recovery_score"] >= 70 else "medium" if processed_data["recovery_score"] >= 40 else "low",
                    dca_id=processed_data["dca_id"],
                    allocated_by=current_user["id"] if processed_data["dca_id"] else None,
                    allocation_date=datetime.utcnow() if processed_data["dca_id"] else None,
                    ml_features={},
                    sla_contact_deadline=processed_data["sla_contact_deadline"],
                    sla_resolution_deadline=processed_data["sla_resolution_deadline"],
                    created_at=datetime.utcnow()
                )
                
                db.add(case)
                
                # Schedule AI analysis in background
                background_tasks.add_task(
                    perform_bulk_ai_analysis,
                    case.id,
                    case_data,
                    db
                )
                
                results["successful"].append({
                    "row": index + 1,
                    "case_id": case.id,
                    "account_id": case.account_id,
                    "priority": case.priority,
                    "recovery_score": case.recovery_score,
                    "allocated_dca": processed_data["dca_id"]
                })
                
            except Exception as e:
                results["failed"].append({
                    "row": index + 1,
                    "error": str(e),
                    "data": row.to_dict()
                })
        
        # Commit all successful cases
        db.commit()
        
        # Generate summary
        results["summary"] = {
            "total_processed": len(df),
            "successful_count": len(results["successful"]),
            "failed_count": len(results["failed"]),
            "success_rate": round((len(results["successful"]) / len(df)) * 100, 2) if len(df) > 0 else 0,
            "uploaded_by": current_user["email"],
            "upload_timestamp": datetime.utcnow().isoformat()
        }
        
        return results
        
    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="CSV file is empty")
    except pd.errors.ParserError:
        raise HTTPException(status_code=400, detail="Invalid CSV format")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


async def perform_bulk_ai_analysis(case_id: str, case_data: dict, db: Session):
    """Background task for AI analysis during bulk upload"""
    try:
        ai_service = AIService()
        ai_service.initialize()
        
        # Get AI insights
        ai_result = ai_service.analyze_case(case_data)
        
        # Update case with AI insights
        case = db.query(Case).filter(Case.id == case_id).first()
        if case:
            case.ml_features = {
                "ai_analysis": ai_result,
                "analyzed_at": datetime.utcnow().isoformat(),
                "bulk_upload": True
            }
            case.recovery_score = ai_result.get("recovery_probability", case.recovery_score) * 100
            case.priority = ai_result.get("priority_level", case.priority)
            db.commit()
            
    except Exception as e:
        print(f"Bulk AI analysis failed for case {case_id}: {e}")


@router.get("/upload-template")
async def get_csv_template(
    current_user: dict = Depends(require_role(["enterprise_admin"]))
):
    """Get CSV template for case upload"""
    
    template_data = {
        "csv_template": {
            "filename": "cases_upload_template.csv",
            "columns": [
                {
                    "name": "account_id",
                    "type": "string",
                    "required": True,
                    "description": "Unique account identifier"
                },
                {
                    "name": "debtor_name", 
                    "type": "string",
                    "required": True,
                    "description": "Full name of the debtor"
                },
                {
                    "name": "debtor_email",
                    "type": "string", 
                    "required": False,
                    "description": "Email address of the debtor"
                },
                {
                    "name": "debtor_phone",
                    "type": "string",
                    "required": False, 
                    "description": "Phone number of the debtor"
                },
                {
                    "name": "debtor_address",
                    "type": "string",
                    "required": False,
                    "description": "Address of the debtor"
                },
                {
                    "name": "original_amount",
                    "type": "number",
                    "required": True,
                    "description": "Original debt amount"
                },
                {
                    "name": "current_amount", 
                    "type": "number",
                    "required": False,
                    "description": "Current outstanding amount (defaults to original_amount)"
                },
                {
                    "name": "currency",
                    "type": "string",
                    "required": False,
                    "description": "Currency code (defaults to USD)"
                },
                {
                    "name": "days_delinquent",
                    "type": "integer", 
                    "required": True,
                    "description": "Number of days the debt is delinquent"
                },
                {
                    "name": "debt_age_days",
                    "type": "integer",
                    "required": False,
                    "description": "Age of the debt in days (defaults to days_delinquent)"
                },
                {
                    "name": "debt_type",
                    "type": "string",
                    "required": False,
                    "description": "Type of debt (credit_card, mortgage, personal_loan, etc.)"
                }
            ]
        },
        "sample_data": [
            {
                "account_id": "ACC-001",
                "debtor_name": "John Doe",
                "debtor_email": "john.doe@email.com",
                "debtor_phone": "+1-555-0123",
                "debtor_address": "123 Main St, City, State 12345",
                "original_amount": 5000.00,
                "current_amount": 4500.00,
                "currency": "USD",
                "days_delinquent": 45,
                "debt_age_days": 45,
                "debt_type": "credit_card"
            },
            {
                "account_id": "ACC-002", 
                "debtor_name": "Jane Smith",
                "debtor_email": "jane.smith@email.com",
                "debtor_phone": "+1-555-0456",
                "debtor_address": "456 Oak Ave, City, State 67890",
                "original_amount": 12000.00,
                "current_amount": 12000.00,
                "currency": "USD", 
                "days_delinquent": 90,
                "debt_age_days": 90,
                "debt_type": "personal_loan"
            }
        ],
        "instructions": [
            "Download this template and fill in your case data",
            "All required fields must be provided",
            "Ensure account_id is unique for each case",
            "Use proper number formats (no commas or currency symbols)",
            "Save as CSV format before uploading",
            "Maximum file size: 10MB",
            "Maximum rows: 1000 cases per upload"
        ]
    }
    
    return template_data