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


class DCASearchParams(BaseSchema):
    """Schema for DCA search parameters"""
    name: Optional[str] = None
    code: Optional[str] = None
    is_active: Optional[bool] = None
    is_accepting_cases: Optional[bool] = None
    min_performance_score: Optional[float] = None
    max_performance_score: Optional[float] = None
    specialization: Optional[List[str]] = None
    min_capacity: Optional[int] = None
    sort_by: Optional[str] = "performance_score"
    sort_order: Optional[str] = "desc"
    
    @validator('sort_by')
    def validate_sort_by(cls, v):
        valid_fields = [
            "name", "code", "performance_score", "recovery_rate", 
            "created_at", "current_active_cases", "sla_compliance_rate"
        ]
        if v not in valid_fields:
            raise ValueError(f'Sort field must be one of: {", ".join(valid_fields)}')
        return v
    
    @validator('sort_order')
    def validate_sort_order(cls, v):
        if v not in ["asc", "desc"]:
            raise ValueError('Sort order must be "asc" or "desc"')
        return v


class DCAStatusUpdate(BaseSchema):
    """Schema for updating DCA status"""
    is_active: Optional[bool] = None
    is_accepting_cases: Optional[bool] = None
    max_concurrent_cases: Optional[int] = None
    reason: Optional[str] = None  # Reason for status change


class DCAPerformanceUpdate(BaseSchema):
    """Schema for manual performance updates"""
    performance_score: Optional[float] = None
    recovery_rate: Optional[float] = None
    avg_resolution_days: Optional[float] = None
    sla_compliance_rate: Optional[float] = None
    notes: Optional[str] = None
    
    @validator('performance_score')
    def validate_performance_score(cls, v):
        if v is not None and (v < 0 or v > 1):
            raise ValueError('Performance score must be between 0 and 1')
        return v
    
    @validator('recovery_rate')
    def validate_recovery_rate(cls, v):
        if v is not None and (v < 0 or v > 100):
            raise ValueError('Recovery rate must be between 0 and 100')
        return v
    
    @validator('sla_compliance_rate')
    def validate_sla_compliance_rate(cls, v):
        if v is not None and (v < 0 or v > 100):
            raise ValueError('SLA compliance rate must be between 0 and 100')
        return v


class DCABulkUpdate(BaseSchema):
    """Schema for bulk DCA updates"""
    dca_ids: List[str]
    updates: DCAUpdate
    
    @validator('dca_ids')
    def validate_dca_ids(cls, v):
        if not v or len(v) == 0:
            raise ValueError('At least one DCA ID must be provided')
        if len(v) > 50:
            raise ValueError('Cannot update more than 50 DCAs at once')
        return v


class DCAStatistics(BaseSchema):
    """Schema for DCA statistics summary"""
    total_dcas: int
    active_dcas: int
    accepting_cases_dcas: int
    avg_performance_score: float
    avg_recovery_rate: float
    total_capacity: int
    total_active_cases: int
    overall_utilization: float
    
    # Performance distribution
    high_performers: int  # > 0.8 performance score
    medium_performers: int  # 0.5 - 0.8
    low_performers: int  # < 0.5
    
    # Capacity distribution
    available_capacity: int
    limited_capacity: int
    at_capacity: int
    over_capacity: int