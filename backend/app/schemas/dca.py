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
    current_active_cases: Optional[int] = 0
    sla_compliance_rate: Optional[float] = None
    is_active: bool
    is_accepting_cases: bool
    onboarded_date: Optional[datetime] = None
    last_performance_update: Optional[datetime] = None


class DCAPerformanceMetrics(BaseSchema):
    """Schema for DCA performance metrics"""
    total_cases_assigned: int
    total_cases_resolved: int
    total_amount_assigned: float
    total_amount_recovered: float
    recovery_rate: float
    avg_resolution_days: float
    sla_compliance_rate: float
    performance_score: float
    
    # Time-based metrics
    cases_this_month: int
    recovery_this_month: float
    cases_last_month: int
    recovery_last_month: float
    
    # Trend indicators
    recovery_trend: str  # "improving", "declining", "stable"
    performance_trend: str
    
    # Breakdown by case priority
    high_priority_recovery_rate: Optional[float] = None
    medium_priority_recovery_rate: Optional[float] = None
    low_priority_recovery_rate: Optional[float] = None


class DCAPerformanceResponse(BaseSchema):
    """Schema for DCA performance API response"""
    dca_id: str
    dca_name: str
    dca_code: str
    period_start: datetime
    period_end: datetime
    metrics: DCAPerformanceMetrics
    last_updated: datetime


class DCACapacityInfo(BaseSchema):
    """Schema for DCA capacity information"""
    dca_id: str
    dca_name: str
    dca_code: str
    max_concurrent_cases: int
    current_active_cases: int
    available_slots: int
    utilization_percentage: float
    is_accepting_cases: bool
    capacity_status: str  # "available", "limited", "full", "overloaded"
    
    @validator('capacity_status', pre=True, always=True)
    def determine_capacity_status(cls, v, values):
        if 'utilization_percentage' in values:
            util = values['utilization_percentage']
            if util >= 100:
                return "overloaded" if util > 100 else "full"
            elif util >= 90:
                return "limited"
            else:
                return "available"
        return v


class DCAAllocationRequest(BaseSchema):
    """Schema for DCA allocation requests"""
    case_ids: List[str]
    dca_id: Optional[str] = None  # If None, auto-allocate
    allocation_strategy: Optional[str] = "intelligent"  # "intelligent", "performance_based", "capacity_based", "round_robin"
    force_allocation: Optional[bool] = False  # Override capacity limits
    
    @validator('allocation_strategy')
    def validate_strategy(cls, v):
        valid_strategies = ["intelligent", "performance_based", "capacity_based", "round_robin"]
        if v not in valid_strategies:
            raise ValueError(f'Strategy must be one of: {", ".join(valid_strategies)}')
        return v
    
    @validator('case_ids')
    def validate_case_ids(cls, v):
        if not v or len(v) == 0:
            raise ValueError('At least one case ID must be provided')
        if len(v) > 100:
            raise ValueError('Cannot allocate more than 100 cases at once')
        return v


class DCAAllocationResponse(BaseSchema):
    """Schema for DCA allocation response"""
    total_cases: int
    allocated_count: int
    failed_count: int
    allocated_cases: List[str]
    failed_cases: List[Dict[str, Any]]
    allocation_summary: Dict[str, Any]


class DCARecommendation(BaseSchema):
    """Schema for DCA allocation recommendations"""
    dca_id: str
    dca_name: str
    dca_code: str
    allocation_score: float
    performance_score: float
    capacity_info: DCACapacityInfo
    specialization_match: float
    recommendation_reason: str
    estimated_resolution_days: Optional[int] = None


class DCARecommendationResponse(BaseSchema):
    """Schema for DCA recommendation API response"""
    case_id: str
    recommendations: List[DCARecommendation]
    total_recommendations: int
    best_match: Optional[DCARecommendation] = None

# TODO: implement edge case handling
