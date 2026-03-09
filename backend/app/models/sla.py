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
# TODO: implement edge case handling
