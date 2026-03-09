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
# TODO: implement edge case handling
