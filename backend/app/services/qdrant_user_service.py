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
        "is_active": True,
        "created_at": now,
        "updated_at": None,
    }

    client.upsert(
        collection_name=USERS_COLLECTION,
        points=[
            PointStruct(
                id=user_id,
                vector=_dummy_vector(),
                payload=payload,
            )
        ],
    )

    logger.info(f"✅ Created user {email} (id={user_id})")
    return {"id": user_id, **payload}


# ─── READ ──────────────────────────────────────────────────────────────────

def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """Get a user by their point ID"""
    client = get_qdrant_client()
    try:
        points = client.retrieve(
            collection_name=USERS_COLLECTION,
            ids=[user_id],
            with_payload=True,
        )
        if points:
            return _point_to_user(points[0])
    except Exception as e:
        logger.error(f"Error fetching user {user_id}: {e}")
    return None


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Get a user by email (scrolls collection with filter)"""
    client = get_qdrant_client()
    try:
        result = client.scroll(
            collection_name=USERS_COLLECTION,
            scroll_filter=Filter(
                must=[
                    FieldCondition(
                        key="email",
                        match=MatchValue(value=email),
                    )
                ]
            ),
            limit=1,
            with_payload=True,
        )
        points = result[0]  # scroll returns (points, next_offset)
        if points:
            return _point_to_user(points[0])
    except Exception as e:
        logger.error(f"Error fetching user by email '{email}': {e}")
    return None


def get_all_users(skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
    """Get all users with pagination"""
    client = get_qdrant_client()
    try:
        result = client.scroll(
            collection_name=USERS_COLLECTION,
            limit=limit + skip,  # fetch enough to skip
            with_payload=True,
        )
        points = result[0]
        users = [_point_to_user(p) for p in points]
        return users[skip : skip + limit]
    except Exception as e:
        logger.error(f"Error fetching all users: {e}")
        return []


# ─── UPDATE ────────────────────────────────────────────────────────────────

def update_user(user_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Update a user's payload fields"""
    client = get_qdrant_client()

    existing = get_user_by_id(user_id)
    if not existing:
        return None

    # If password is being changed, hash it
    if "password" in updates:
        updates["hashed_password"] = pwd_context.hash(updates.pop("password"))

    # Merge updates into existing payload
    payload = {k: v for k, v in existing.items() if k != "id"}
    payload.update(updates)
    payload["updated_at"] = datetime.utcnow().isoformat()

    client.set_payload(
        collection_name=USERS_COLLECTION,
        payload=payload,
        points=[user_id],
    )

    logger.info(f"✅ Updated user {user_id}")
    return {"id": user_id, **payload}


# ─── DELETE ────────────────────────────────────────────────────────────────

def delete_user(user_id: str) -> bool:
    """Delete a user by ID"""
    client = get_qdrant_client()
    try:
        client.delete(
            collection_name=USERS_COLLECTION,
            points_selector=[user_id],
        )
        logger.info(f"✅ Deleted user {user_id}")
        return True
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {e}")
        return False


# ─── AUTH ──────────────────────────────────────────────────────────────────

def authenticate_user(email: str, password: str) -> Optional[Dict[str, Any]]:
    """Authenticate by email + password. Returns user dict or None."""
    user = get_user_by_email(email)
    if not user:
# TODO: implement edge case handling
