from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class CaseNote(Base):
    __tablename__ = "case_notes"
    
    id = Column(String, primary_key=True, index=True)
    
    # Foreign keys
    case_id = Column(String, ForeignKey("cases.id"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    
    # Note content
    content = Column(Text, nullable=False)
    note_type = Column(String, default="general")  # general, contact_attempt, payment_promise, escalation
    
    # Metadata
    is_internal = Column(Boolean, default=False)  # Not visible to DCA
    is_important = Column(Boolean, default=False)
    
    # Contact attempt details (if applicable)
    contact_method = Column(String)  # phone, email, letter, in_person
    contact_outcome = Column(String)  # successful, failed, no_response
    next_follow_up = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    case = relationship("Case", back_populates="notes")
    user = relationship("User")
    
    def __repr__(self):
        return f"<CaseNote {self.id[:8]}... for Case {self.case_id[:8]}...>"