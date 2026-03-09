"""
SIMPLE DATABASE SETUP FOR HACKATHON - NO ALEMBIC
"""
import sys
import os
from pathlib import Path

print("=" * 60)
print("RINEXOR - DATABASE SETUP")
print("=" * 60)

# Add current directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    # Import database engine and models
    from app.core.database import engine, Base
    from app.models import *
    
    print("✅ Imported all models successfully")
    
    # CREATE ALL TABLES
    print("\n📦 Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created!")
    
    # VERIFY TABLES
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    print(f"\n📊 Found {len(tables)} tables:")
    print("-" * 40)
    for table in sorted(tables):
        print(f"  • {table}")
    
    # CREATE DEMO DATA
    print("\n🎭 Creating demo data...")
    from sqlalchemy.orm import Session
    from app.models.user import User, UserRole
    from app.models.dca import DCA
    from app.models.case import Case, CaseStatus, CasePriority, RecoveryScoreBand
    import uuid
    from datetime import datetime, timedelta
    import random
    
    db = Session(engine)
    
    # 1. Create DCAs
    dcas = []
    dca_names = [
        ("Alpha Collections", "John Manager", "contact@alphacollections.com"),
        ("Beta Recovery", "Sarah Smith", "contact@betarecovery.com"),
        ("Gamma Solutions", "Mike Johnson", "info@gammasolutions.com"),
        ("Delta Agency", "Lisa Chen", "support@deltaagency.com")
    ]
    
    for i, (name, contact, email) in enumerate(dca_names):
        dca = DCA(
            id=str(uuid.uuid4()),
            name=name,
# TODO: implement edge case handling
