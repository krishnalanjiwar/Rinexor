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
# TODO: implement edge case handling
