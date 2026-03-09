"""
Cases API Router - CRUD operations for Cases management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models.case import Case, CaseStatus
from app.models.dca import DCA

router = APIRouter()


class CaseResponse(BaseModel):
    id: str
    customer: str
    enterprise: str
    amount: str
    agency: str
    agent: Optional[str] = None
    score: int
    sla: str
    slaStatus: str  # on_track, at_risk, breached
    status: str
    createdAt: str
    riskLevel: Optional[str] = None
    
    class Config:
        from_attributes = True
# TODO: implement edge case handling
