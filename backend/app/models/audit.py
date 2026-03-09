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
# TODO: implement edge case handling
