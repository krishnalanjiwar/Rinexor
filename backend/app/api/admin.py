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

# TODO: implement edge case handling
