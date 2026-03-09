"""
TEST SCRIPT - Checks if everything works
"""
import sys
import os

print("Testing server setup...")

# Check imports
try:
    from app.core.config import settings
    print("✅ Config imported")
    
    from app.core.database import engine, Base
    print("✅ Database imported")
    
    # Try to create tables
    from app.models import *
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables verified")
    
    print("\n✅ ALL CHECKS PASSED!")
    print("\nStart server with:")
    print("  cd backend")
    print("  python -m uvicorn app.main:app --reload")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("\nMissing packages. Install with:")
    print("  pip install fastapi uvicorn sqlalchemy")
    
except Exception as e:
    print(f"❌ Error: {e}")