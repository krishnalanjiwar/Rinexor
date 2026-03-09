from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class DocumentType(str, enum.Enum):
    AGREEMENT = "agreement"
    PROOF_OF_DEBT = "proof_of_debt"
    COMMUNICATION = "communication"
    PAYMENT_RECEIPT = "payment_receipt"
    ID_PROOF = "id_proof"
    OTHER = "other"

class DocumentStatus(str, enum.Enum):
    UPLOADED = "uploaded"
    VERIFIED = "verified"
    REJECTED = "rejected"
    DELETED = "deleted"

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(String, primary_key=True, index=True)
    
    # Foreign keys
    case_id = Column(String, ForeignKey("cases.id"), nullable=False, index=True)
    uploaded_by = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Document metadata
    filename = Column(String, nullable=False)
    file_type = Column(Enum(DocumentType), default=DocumentType.OTHER)
    file_path = Column(String, nullable=False)  # Path in storage (S3/local)
    file_size = Column(Integer)  # In bytes
    mime_type = Column(String)
    
    # Status and verification
    status = Column(Enum(DocumentStatus), default=DocumentStatus.UPLOADED)
    verified_by = Column(String, ForeignKey("users.id"), nullable=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    # Description
    description = Column(Text)
    tags = Column(JSON, default=list)  # e.g., ["agreement", "signed", "scan"]
    
    # Timestamps
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    case = relationship("Case", back_populates="documents")
    uploader = relationship("User", foreign_keys=[uploaded_by])
    verifier = relationship("User", foreign_keys=[verified_by])
    
    def __repr__(self):
        return f"<Document {self.filename} for Case {self.case_id[:8]}...>"