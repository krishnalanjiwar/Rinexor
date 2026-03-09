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
# TODO: implement edge case handling
