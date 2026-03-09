"""
USERS API - User management endpoints backed by SQLite
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List

from app.api.auth import get_current_user

router = APIRouter()


# ─── Schemas ───────────────────────────────────────────────────────────────

class UserCreateRequest(BaseModel):
    email: str
    password: str
    name: str
    role: str = "dca_agent"
    dca_id: Optional[str] = None


class UserUpdateRequest(BaseModel):
    email: Optional[str] = None
    name: Optional[str] = None
    role: Optional[str] = None
    dca_id: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None


class CreateAdminRequest(BaseModel):
    role: str  # "enterprise_admin" or "dca_agent"

# TODO: implement edge case handling
