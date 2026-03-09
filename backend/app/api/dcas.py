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
                "email": "john@newrecovery.com",
                "phone": "+91-9876543210",
                "address": "Mumbai, India",
                "max_concurrent_cases": 100,
                "specialization": ["personal_loans", "credit_cards"]
            }
        }


class DCAUpdate(BaseModel):
    name: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    max_concurrent_cases: Optional[int] = None
    specialization: Optional[List[str]] = None
    is_active: Optional[bool] = None
    is_accepting_cases: Optional[bool] = None


class DCAResponse(BaseModel):
    id: str
    name: str
    code: str
    contact_person: str
    email: str
    phone: Optional[str]
    address: Optional[str]
    performance_score: float
    recovery_rate: float
    avg_resolution_days: float
    max_concurrent_cases: int
    current_active_cases: int
    specialization: Optional[List[str]]
    sla_compliance_rate: float
    is_active: bool
    is_accepting_cases: bool
    onboarded_date: Optional[datetime]
    
    class Config:
        from_attributes = True


@router.get("/", response_model=List[DCAResponse])
async def get_all_dcas(
    active_only: bool = False,
    db: Session = Depends(get_db)
):
    """Get all DCAs, optionally filtered by active status"""
    query = db.query(DCA)
    
    if active_only:
        query = query.filter(DCA.is_active == True)
    
    dcas = query.order_by(DCA.performance_score.desc()).all()
    return dcas


@router.get("/{dca_id}", response_model=DCAResponse)
async def get_dca(
    dca_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific DCA by ID"""
    dca = db.query(DCA).filter(DCA.id == dca_id).first()
    
    if not dca:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="DCA not found"
        )
    
    return dca


@router.post("/", response_model=DCAResponse, status_code=status.HTTP_201_CREATED)
async def create_dca(
    dca_data: DCACreate,
    db: Session = Depends(get_db)
):
    """Create a new DCA (Onboard New Agency)"""
    # Check if code already exists
    existing = db.query(DCA).filter(DCA.code == dca_data.code).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"DCA with code '{dca_data.code}' already exists"
        )
    
    # Check if name already exists
    existing_name = db.query(DCA).filter(DCA.name == dca_data.name).first()
    if existing_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"DCA with name '{dca_data.name}' already exists"
        )
    
    # Create new DCA
# TODO: implement edge case handling
