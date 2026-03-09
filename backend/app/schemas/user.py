"""
USER SCHEMAS - Pydantic models for user API requests/responses
"""
from pydantic import BaseModel, EmailStr, validator
from typing import Optional, Literal
from datetime import datetime

from app.schemas.base import BaseSchema, IDSchema, TimestampSchema

# Define user roles as Literal type for Pydantic
UserRoleType = Literal["enterprise_admin", "collection_manager", "dca_agent"]


class UserBase(BaseSchema):
    email: EmailStr
    full_name: str
    role: UserRoleType
    dca_id: Optional[str] = None
    is_active: bool = True
    
    @validator('full_name')
    def validate_full_name(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('Full name must be at least 2 characters')
        return v.strip()


class UserCreate(UserBase):
    """Schema for creating a new user"""
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters')
        return v
# TODO: implement edge case handling
