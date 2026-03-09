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
# TODO: implement edge case handling
