from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import json

from app.core.database import get_db
from app.core.security import get_current_user, require_role, decode_token
from app.services.ai_service import AIService
from app.models.case import Case

router = APIRouter()

# Optional OAuth2 scheme (doesn't fail if no token)
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)

async def get_optional_user(token: Optional[str] = Depends(oauth2_scheme_optional)) -> Dict[str, Any]:
    """Get current user if token provided, otherwise return test user for demo"""
    if token:
        payload = decode_token(token)
        if payload:
            return payload
    # Return a default test user for demo/testing
    return {
        "id": "test_user",
        "email": "test@demo.com",
        "role": "enterprise_admin"
    }

# Initialize AI service
ai_service = AIService()
ai_service.initialize()


@router.post("/analyze-case")
async def analyze_case(
    case_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Analyze a single case with AI"""
    try:
        result = ai_service.analyze_case(case_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")

@router.post("/analyze-portfolio")
async def analyze_portfolio(
    case_ids: List[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Analyze portfolio of cases with AI"""
    try:
        if case_ids:
            # Get specific cases
            cases = db.query(Case).filter(Case.id.in_(case_ids)).all()
            case_dicts = [case.__dict__ for case in cases]
        else:
            # Get all cases user has access to
            query = db.query(Case)
            
            if current_user["role"] == "dca_agent":
                query = query.filter(Case.dca_id == current_user.get("dca_id"))
            elif current_user["role"] == "collection_manager":
                if current_user.get("dca_id"):
                    query = query.filter(Case.dca_id == current_user.get("dca_id"))
            
            cases = query.all()
            case_dicts = [case.__dict__ for case in cases]
        
        # Remove SQLAlchemy instance state
        for case in case_dicts:
            if '_sa_instance_state' in case:
                del case['_sa_instance_state']
        
        result = ai_service.analyze_portfolio(case_dicts)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Portfolio analysis failed: {str(e)}")

@router.get("/patterns")
async def detect_patterns(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role(["enterprise_admin", "collection_manager"]))
):
    """Detect patterns in case data"""
    try:
        # Get all cases
        query = db.query(Case)
        
        if current_user["role"] == "collection_manager" and current_user.get("dca_id"):
            query = query.filter(Case.dca_id == current_user.get("dca_id"))
        
        cases = query.all()
        case_dicts = [case.__dict__ for case in cases]
        
        # Remove SQLAlchemy instance state
        for case in case_dicts:
            if '_sa_instance_state' in case:
                del case['_sa_instance_state']
        
        from app.ml.pattern_detector import PatternDetector
        patterns = PatternDetector.detect_recovery_patterns(case_dicts)
        
        return patterns
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pattern detection failed: {str(e)}")

@router.post("/train-model")
async def train_ai_model(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role(["enterprise_admin"]))
):
    """Train the AI model with current data"""
    try:
        # Get historical data for training
        cases = db.query(Case).filter(Case.status == "resolved").all()
        
        if len(cases) < 10:
            return {
                "success": False,
                "message": f"Need at least 10 resolved cases for training. Found {len(cases)}.",
                "suggestion": "Use mock data for demo"
            }
        
        # Prepare training data
        training_data = []
        for case in cases:
            case_dict = {
                "original_amount": case.original_amount,
                "days_delinquent": case.days_delinquent,
                "recovery_rate": ((case.original_amount - case.current_amount) / case.original_amount) * 100
            }
            training_data.append(case_dict)
        
        # Train model
        result = ai_service.train_model(training_data)
        
        return {
            "success": result["success"],
            "message": "AI model trained successfully" if result["success"] else "Training failed",
            "details": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model training failed: {str(e)}")

@router.get("/model-status")
async def get_model_status(
    current_user: dict = Depends(get_current_user)
):
    """Get AI model status"""
    try:
        import os
        model_exists = os.path.exists("ml_models/recovery_model.pkl")
        
        return {
            "model_trained": model_exists,
            "model_path": "ml_models/recovery_model.pkl" if model_exists else None,
            "ai_service_initialized": True,
            "using_rule_based": not model_exists,
            "message": "Using trained AI model" if model_exists else "Using rule-based fallback"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get model status: {str(e)}")

@router.post("/prioritize-cases")
async def prioritize_cases(
    case_data_list: List[Dict[str, Any]],
    current_user: dict = Depends(get_current_user)
):
    """Prioritize multiple cases"""
    try:
        from app.ml.priority_engine import PriorityEngine
        prioritized = PriorityEngine.batch_prioritize(case_data_list)
        
        return {
            "total_cases": len(prioritized),
            "prioritized_cases": prioritized[:50],  # Return top 50
            "high_priority_count": sum(1 for c in prioritized if c["priority_level"] == "high"),
            "medium_priority_count": sum(1 for c in prioritized if c["priority_level"] == "medium"),
            "low_priority_count": sum(1 for c in prioritized if c["priority_level"] == "low")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prioritization failed: {str(e)}")


# ============== NEW RISK-BASED ALLOCATION ENDPOINTS ==============

from fastapi import UploadFile, File

# Store for temporary file analysis results (in production, use Redis or database)
_analysis_cache: Dict[str, Dict[str, Any]] = {}


@router.post("/upload-cases")
async def upload_cases_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_optional_user)
):
    """
    Upload a CSV or Excel file containing case data.
    Returns parsed case data with validation status.
    """
    try:
        # Read file content
        content = await file.read()
        filename = file.filename or "upload.csv"
        
        # Parse file
        result = ai_service.parse_uploaded_file(content, filename)
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result.get('error', 'File parsing failed'))
        
# TODO: implement edge case handling
