"""
DCA SCHEMAS - Pydantic models for DCA API requests/responses
"""
from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.schemas.base import BaseSchema, IDSchema, TimestampSchema


class DCABase(BaseSchema):
    name: str
    code: str
    contact_person: str
    email: EmailStr
    phone: Optional[str] = None
    address: Optional[str] = None
    specialization: Optional[List[str]] = []
    max_concurrent_cases: Optional[int] = 50
    
    @validator('code')
    def validate_code(cls, v):
        if not v or len(v) < 3:
            raise ValueError('DCA code must be at least 3 characters')
        return v.upper()
    
    @validator('name')
    def validate_name(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('DCA name must be at least 2 characters')
        return v.strip()


class DCACreate(DCABase):
    """Schema for creating a new DCA"""
    pass


class DCAUpdate(BaseSchema):
    """Schema for updating an existing DCA"""
    name: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    specialization: Optional[List[str]] = None
    max_concurrent_cases: Optional[int] = None
    is_active: Optional[bool] = None
    is_accepting_cases: Optional[bool] = None
    
    @validator('name')
    def validate_name(cls, v):
        if v is not None and len(v.strip()) < 2:
            raise ValueError('DCA name must be at least 2 characters')
        return v.strip() if v else v


class DCAResponse(DCABase, IDSchema, TimestampSchema):
    """Schema for DCA API responses"""
    performance_score: float
    recovery_rate: float
    avg_resolution_days: Optional[float] = None
# TODO: implement edge case handling
