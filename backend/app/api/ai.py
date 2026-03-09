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
# TODO: implement edge case handling
