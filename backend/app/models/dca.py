from sqlalchemy import Column, String, Float, DateTime, Boolean, Integer, JSON, Text
from sqlalchemy.sql import func
from app.core.database import Base

class DCA(Base):
    __tablename__ = "dcas"
    
    id = Column(String, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    code = Column(String, unique=True, nullable=False)
    contact_person = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String)
    address = Column(Text)
    performance_score = Column(Float, default=0.0)
    recovery_rate = Column(Float, default=0.0)
    avg_resolution_days = Column(Float, default=0.0)
    max_concurrent_cases = Column(Integer, default=50)
    current_active_cases = Column(Integer, default=0)
    specialization = Column(JSON)  # List of specializations
    sla_compliance_rate = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    is_accepting_cases = Column(Boolean, default=True)
    onboarded_date = Column(DateTime)
    last_performance_update = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    def __repr__(self):
        return f"<DCA {self.code}>"