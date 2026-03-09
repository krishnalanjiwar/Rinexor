from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base


class UserRole:
    ENTERPRISE_ADMIN = "enterprise_admin"
    COLLECTION_MANAGER = "collection_manager"
    DCA_AGENT = "dca_agent"


class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    role = Column(String, nullable=False)
    dca_id = Column(String, ForeignKey("dcas.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    def __repr__(self):
        return f"<User {self.email}>"