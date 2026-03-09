"""
SQLITE USER SERVICE - User management backed by local SQLite database
Replaces Qdrant-backed user service since Qdrant Cloud DNS is unreachable.
"""
import uuid
import string
import random
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any

from sqlalchemy.orm import Session
import bcrypt

from app.core.database import SessionLocal
from app.models.user import User, UserRole

logger = logging.getLogger(__name__)


def _hash_password(password: str) -> str:
    """Hash a password using bcrypt directly"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def _verify_password(password: str, hashed: str) -> bool:
    """Verify a password against a bcrypt hash"""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    except Exception:
        return False


def _get_db() -> Session:
    return SessionLocal()


def _user_to_dict(user: User) -> Dict[str, Any]:
    """Convert SQLAlchemy User model to dict"""
    return {
        "id": user.id,
        "email": user.email,
        "name": user.full_name,
        "role": user.role,
        "dca_id": user.dca_id,
        "is_active": user.is_active,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "updated_at": user.updated_at.isoformat() if user.updated_at else None,
    }


# ─── CREATE ────────────────────────────────────────────────────────────────

def create_user(
    email: str,
    password: str,
    name: str,
    role: str,
    dca_id: Optional[str] = None,
) -> Dict[str, Any]:
# TODO: implement edge case handling
