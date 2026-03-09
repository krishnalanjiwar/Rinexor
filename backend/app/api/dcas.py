"""
DCA API Router - CRUD operations for DCA (Debt Collection Agency) management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

from app.core.database import get_db
from app.models.dca import DCA

router = APIRouter()


# Pydantic models for request/response
class DCACreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    code: str = Field(..., min_length=2, max_length=20)
    contact_person: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., min_length=5, max_length=100)
    phone: Optional[str] = None
    address: Optional[str] = None
    max_concurrent_cases: int = Field(default=50, ge=1, le=1000)
    specialization: Optional[List[str]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "New Recovery Agency",
                "code": "NRA001",
                "contact_person": "John Doe",
# TODO: implement edge case handling
