"""
QDRANT USER SERVICE - CRUD operations for users stored in Qdrant Cloud
"""
import uuid
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any

from qdrant_client import QdrantClient
from qdrant_client.models import (
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    ScrollRequest,
)
from passlib.context import CryptContext

from app.core.qdrant_db import get_qdrant_client, USERS_COLLECTION, VECTOR_SIZE

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _dummy_vector() -> List[float]:
    """Generate a small dummy vector (Qdrant requires vectors per point)"""
    return [0.0] * VECTOR_SIZE


def _point_to_user(point) -> Dict[str, Any]:
    """Convert a Qdrant point to a user dict"""
    user = dict(point.payload)
    user["id"] = str(point.id) if point.id else user.get("id")
    return user


# ─── CREATE ────────────────────────────────────────────────────────────────

def create_user(
    email: str,
    password: str,
    name: str,
    role: str,
    enterprise_id: Optional[str] = None,
    dca_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a new user in Qdrant Cloud"""
    client = get_qdrant_client()

    # Check if email already exists
    existing = get_user_by_email(email)
    if existing:
        raise ValueError(f"User with email '{email}' already exists")

    user_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()

    payload = {
        "email": email,
        "hashed_password": pwd_context.hash(password),
        "name": name,
        "role": role,
        "enterprise_id": enterprise_id,
        "dca_id": dca_id,
# TODO: implement edge case handling
