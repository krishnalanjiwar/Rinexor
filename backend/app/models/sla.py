from sqlalchemy import Column, String, Text, DateTime, Boolean, Integer, Float, JSON, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class SLARuleType(str, enum.Enum):
    CASE_ASSIGNMENT = "case_assignment"
    CONTACT_DEADLINE = "contact_deadline"
    RESOLUTION_DEADLINE = "resolution_deadline"
    ESCALATION = "escalation"
    FOLLOW_UP = "follow_up"

class SLAAction(str, enum.Enum):
    NOTIFY = "notify"
    ESCALATE = "escalate"
    REASSIGN = "reassign"
    PENALIZE = "penalize"
    AUTO_CLOSE = "auto_close"

class SLARule(Base):
    __tablename__ = "sla_rules"
    
    id = Column(String, primary_key=True, index=True)
    
    # Rule identification
    name = Column(String, nullable=False, unique=True)
    description = Column(Text)
    rule_type = Column(Enum(SLARuleType), nullable=False)
    
    # Conditions (stored as JSON for flexibility)
    conditions = Column(JSON, nullable=False)
    # Example: {"priority": ["high", "medium"], "days_delinquent": {"gt": 60}}
    
    # Timing
    trigger_delay_days = Column(Integer, default=0)  # Days after trigger event
    trigger_delay_hours = Column(Integer, default=0)  # Hours after trigger event
    
    # Actions to take when triggered
    actions = Column(JSON, nullable=False)
    # Example: [{"action": "notify", "recipients": ["admin"], "template": "sla_breach"}]
    
    # Escalation chain
    escalation_level = Column(Integer, default=1)
    next_escalation_rule_id = Column(String, ForeignKey("sla_rules.id"), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_triggered = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<SLARule {self.name} ({self.rule_type})>"

class SLABreach(Base):
    __tablename__ = "sla_breaches"
    
    id = Column(String, primary_key=True, index=True)
    
    # What was breached
    case_id = Column(String, ForeignKey("cases.id"), nullable=False, index=True)
    breach_type = Column(String, nullable=False)  # "contact_sla" or "resolution_sla"
    
    # Breach details
    detected_at = Column(DateTime, server_default=func.now())
    deadline = Column(DateTime, nullable=False)
    days_overdue = Column(Integer, nullable=False)
    
    # Resolution
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(String, ForeignKey("users.id"), nullable=True)
    resolution_notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    
    def __repr__(self):
        return f"<SLABreach for Case {self.case_id[:8]}... Type {self.breach_type}>"