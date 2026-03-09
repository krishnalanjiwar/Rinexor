"""
Script to create database tables and seed initial DCA data
"""
import sys
sys.path.append('.')

from app.core.database import engine, Base, SessionLocal
from app.models.dca import DCA
from app.models.case import Case
from datetime import datetime
import uuid

def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully!")

def seed_dcas():
    """Seed sample DCA data"""
    db = SessionLocal()
    
    # Check if DCAs already exist
    existing = db.query(DCA).first()
    if existing:
        print("DCAs already exist, skipping seed...")
        db.close()
        return
    
    print("Seeding DCA data...")
    
    sample_dcas = [
        {
            "id": str(uuid.uuid4()),
            "name": "Alpha Collections India",
            "code": "ACI001",
            "contact_person": "Rahul Sharma",
            "email": "rahul@alphacollections.in",
            "phone": "+91-9876543210",
            "address": "Mumbai, Maharashtra",
            "performance_score": 0.85,
            "recovery_rate": 0.72,
            "avg_resolution_days": 45.5,
            "max_concurrent_cases": 100,
            "current_active_cases": 25,
            "specialization": ["personal_loans", "credit_cards"],
            "sla_compliance_rate": 0.92,
            "is_active": True,
            "is_accepting_cases": True,
            "onboarded_date": datetime(2024, 1, 15),
            "last_performance_update": datetime.now()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Beta Recovery Services",
            "code": "BRS002",
            "contact_person": "Priya Patel",
            "email": "priya@betarecovery.in",
            "phone": "+91-9876543211",
            "address": "Bangalore, Karnataka",
            "performance_score": 0.78,
            "recovery_rate": 0.65,
            "avg_resolution_days": 52.3,
            "max_concurrent_cases": 75,
            "current_active_cases": 18,
            "specialization": ["auto_loans", "mortgages"],
            "sla_compliance_rate": 0.88,
            "is_active": True,
            "is_accepting_cases": True,
            "onboarded_date": datetime(2024, 3, 20),
            "last_performance_update": datetime.now()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Gamma Debt Solutions",
            "code": "GDS003",
            "contact_person": "Amit Kumar",
            "email": "amit@gammadebt.in",
            "phone": "+91-9876543212",
            "address": "Delhi NCR",
            "performance_score": 0.92,
            "recovery_rate": 0.80,
            "avg_resolution_days": 38.7,
            "max_concurrent_cases": 150,
            "current_active_cases": 45,
            "specialization": ["personal_loans", "business_loans", "credit_cards"],
            "sla_compliance_rate": 0.95,
            "is_active": True,
            "is_accepting_cases": True,
            "onboarded_date": datetime(2023, 11, 10),
            "last_performance_update": datetime.now()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Delta Financial Recovery",
            "code": "DFR004",
            "contact_person": "Sunita Reddy",
            "email": "sunita@deltafinancial.in",
            "phone": "+91-9876543213",
            "address": "Hyderabad, Telangana",
            "performance_score": 0.70,
            "recovery_rate": 0.55,
            "avg_resolution_days": 60.2,
            "max_concurrent_cases": 50,
            "current_active_cases": 12,
            "specialization": ["small_business", "auto_loans"],
            "sla_compliance_rate": 0.82,
            "is_active": True,
            "is_accepting_cases": True,
            "onboarded_date": datetime(2024, 5, 1),
            "last_performance_update": datetime.now()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Epsilon Collections Agency",
            "code": "ECA005",
            "contact_person": "Vijay Menon",
            "email": "vijay@epsiloncollect.in",
            "phone": "+91-9876543214",
            "address": "Chennai, Tamil Nadu",
            "performance_score": 0.82,
            "recovery_rate": 0.68,
            "avg_resolution_days": 48.5,
            "max_concurrent_cases": 80,
            "current_active_cases": 30,
            "specialization": ["mortgages", "personal_loans"],
            "sla_compliance_rate": 0.90,
            "is_active": True,
            "is_accepting_cases": True,
            "onboarded_date": datetime(2024, 2, 28),
            "last_performance_update": datetime.now()
        }
    ]
    
    for dca_data in sample_dcas:
        dca = DCA(**dca_data)
        db.add(dca)
    
    db.commit()
    print(f"✅ Seeded {len(sample_dcas)} DCAs successfully!")
    db.close()

if __name__ == "__main__":
    create_tables()
# TODO: implement edge case handling
