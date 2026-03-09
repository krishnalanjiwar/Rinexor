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
# TODO: implement edge case handling
