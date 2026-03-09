import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.core.database import SessionLocal, engine
from app.models import *
from sqlalchemy.orm import Session
import uuid
from datetime import datetime, timedelta
import random

def seed_database(db: Session):
    print("🌱 Seeding database...")
    
    # Clear existing data (for demo only)
    db.query(User).delete()
    db.query(DCA).delete()
    db.query(Case).delete()
    db.commit()
    
    # Create DCAs
    dcas = []
    dca_names = ["Alpha Collections", "Beta Recovery", "Gamma Solutions", "Delta Agency"]
    
    for i, name in enumerate(dca_names):
        dca = DCA(
            id=str(uuid.uuid4()),
            name=name,
            code=f"DCA-{i+1:03d}",
            contact_person=f"Manager {i+1}",
            email=f"contact@{name.lower().replace(' ', '')}.com",
            phone=f"+1-555-{1000+i}",
            address=f"{i+1} Collection Street, City, State",
# TODO: implement edge case handling
