from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum, JSON, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class AuditAction(str, enum.Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    ASSIGN = "assign"
    ESCALATE = "escalate"
    STATUS_CHANGE = "status_change"
    LOGIN = "login"
    LOGOUT = "logout"

class AuditEntityType(str, enum.Enum):
    CASE = "case"
    USER = "user"
    DCA = "dca"
    NOTE = "note"
    DOCUMENT = "document"

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(String, primary_key=True, index=True)
    
    # Who performed the action
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    user_ip = Column(String)
    user_agent = Column(Text)
    
    # What action was performed
    action = Column(Enum(AuditAction), nullable=False)
    entity_type = Column(Enum(AuditEntityType), nullable=False)
    entity_id = Column(String, nullable=False, index=True)
    
    # Change details
    old_values = Column(JSON, default=dict)
    new_values = Column(JSON, default=dict)
    changes = Column(JSON, default=dict)  # Computed diff
    
    # Additional context
    description = Column(Text)
    route = Column(String)  # API endpoint
    request_id = Column(String)  # For tracking across microservices
    
    # Timestamps
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
    case = relationship("Case", back_populates="audit_logs", foreign_keys=[entity_id], primaryjoin="and_(AuditLog.entity_id==Case.id, AuditLog.entity_type=='case')")
    
    # Indexes
    __table_args__ = (
        Index('idx_audit_entity', 'entity_type', 'entity_id'),
        Index('idx_audit_timestamp', 'timestamp'),
        Index('idx_audit_user_action', 'user_id', 'action'),
    )
    
    def __repr__(self):
        return f"<AuditLog {self.action} {self.entity_type} {self.entity_id[:8]}...>"