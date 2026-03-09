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
# TODO: implement edge case handling
