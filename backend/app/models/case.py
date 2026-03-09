from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text, Boolean, JSON
from sqlalchemy.sql import func
from app.core.database import Base


class CaseStatus:
    NEW = "new"
    ALLOCATED = "allocated"
    IN_PROGRESS = "in_progress"
    ESCALATED = "escalated"
    RESOLVED = "resolved"
    RETURNED = "returned"
    CLOSED = "closed"


class CasePriority:
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RecoveryScoreBand:
    HIGH = "high"  # 70-100%
    MEDIUM = "medium"  # 40-69%
    LOW = "low"  # 0-39%


class Case(Base):
    __tablename__ = "cases"
    
    id = Column(String, primary_key=True)
    account_id = Column(String, nullable=False)
    debtor_name = Column(String, nullable=False)
    debtor_email = Column(String)
    debtor_phone = Column(String)
    debtor_address = Column(Text)
    original_amount = Column(Float, nullable=False)
    current_amount = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    days_delinquent = Column(Integer, default=0)
    debt_age_days = Column(Integer, default=0)
    status = Column(String, default=CaseStatus.NEW)
    priority = Column(String, default=CasePriority.MEDIUM)
    recovery_score = Column(Float, default=0.0)
    recovery_score_band = Column(String, default=RecoveryScoreBand.MEDIUM)
    dca_id = Column(String, ForeignKey("dcas.id"))
    allocated_by = Column(String, ForeignKey("users.id"))
    allocation_date = Column(DateTime)
    first_contact_date = Column(DateTime)
    last_contact_date = Column(DateTime)
    resolved_date = Column(DateTime)
    sla_contact_deadline = Column(DateTime)
    sla_resolution_deadline = Column(DateTime)
    ml_features = Column(JSON)  # Store AI/ML analysis results
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    def __repr__(self):
        return f"<Case {self.account_id}>"