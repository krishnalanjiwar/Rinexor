"""
Seed Qdrant Cloud with demo users for Rinexor.

Run:  python seed_qdrant_users.py
"""
import sys
sys.path.append(".")

from dotenv import load_dotenv
load_dotenv()

from app.core.qdrant_db import get_qdrant_client, ensure_collections
from app.services.qdrant_user_service import create_user, get_user_by_email

DEMO_USERS = [
    {
        "email": "admin@rinexor.com",
        "password": "admin123",
        "name": "Super Admin",
        "role": "super_admin",
        "enterprise_id": None,
        "dca_id": None,
    },
    {
        "email": "enterprise@demo.com",
        "password": "enterprise123",
        "name": "Enterprise Admin",
        "role": "enterprise_admin",
        "enterprise_id": "ent-001",
        "dca_id": None,
    },
    {
        "email": "dca@demo.com",
# TODO: implement edge case handling
