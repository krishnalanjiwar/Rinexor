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
# TODO: implement edge case handling
