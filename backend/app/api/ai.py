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
# TODO: implement edge case handling
