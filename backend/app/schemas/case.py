from pydantic import BaseModel, Field, validator
from typing import Optional, List, Literal
from datetime import datetime
from .base import BaseSchema, TimestampSchema

# Define status and priority as Literal types for Pydantic
CaseStatusType = Literal["new", "allocated", "in_progress", "escalated", "resolved", "returned", "closed"]
CasePriorityType = Literal["high", "medium", "low"]
RecoveryScoreBandType = Literal["high", "medium", "low"]

class CaseBase(BaseSchema):
    account_id: str = Field(..., description="Unique account identifier")
    debtor_name: str = Field(..., min_length=2, max_length=100)
    debtor_email: Optional[str] = None
    debtor_phone: Optional[str] = None
    debtor_address: Optional[str] = None
    original_amount: float = Field(..., gt=0, description="Original debt amount")
    current_amount: float = Field(..., gt=0, description="Current outstanding amount")
    currency: str = "USD"
    days_delinquent: int = Field(0, ge=0)
    debt_age_days: int = Field(..., ge=0)

class CaseCreate(CaseBase):
    pass

class CaseUpdate(BaseSchema):
    status: Optional[CaseStatusType] = None
    priority: Optional[CasePriorityType] = None
    current_amount: Optional[float] = None
    dca_id: Optional[str] = None
    recovery_score: Optional[float] = Field(None, ge=0, le=100)
    
    @validator('current_amount')
    def validate_current_amount(cls, v):
        if v is not None and v < 0:
            raise ValueError('Current amount cannot be negative')
        return v

class CaseInDB(CaseBase, TimestampSchema):
    id: str
    status: CaseStatusType
    priority: CasePriorityType
    recovery_score: float
    recovery_score_band: RecoveryScoreBandType
    dca_id: Optional[str]
    allocated_by: Optional[str]
    allocation_date: Optional[datetime]
    ml_features: Optional[dict] = {}
    sla_contact_deadline: Optional[datetime]
    sla_resolution_deadline: Optional[datetime]
    first_contact_date: Optional[datetime] = None
    resolved_date: Optional[datetime] = None

class CaseResponse(CaseInDB):
    dca_name: Optional[str] = None
    allocated_by_name: Optional[str] = None
    
class CaseAllocationRequest(BaseSchema):
    case_ids: List[str]
    dca_id: str
    allocation_reason: Optional[str] = None
    
class CaseSearchParams(BaseSchema):
    status: Optional[CaseStatusType] = None
    priority: Optional[CasePriorityType] = None
    dca_id: Optional[str] = None
    recovery_score_min: Optional[float] = None
    recovery_score_max: Optional[float] = None
    days_delinquent_min: Optional[int] = None
    days_delinquent_max: Optional[int] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    search_text: Optional[str] = None