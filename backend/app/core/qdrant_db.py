"""
QDRANT CLIENT - Singleton connection to Qdrant Cloud
"""
import logging
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from app.core.config import settings

logger = logging.getLogger(__name__)

# Singleton client instance
_qdrant_client: QdrantClient = None

# Collection names
USERS_COLLECTION = "users"

# Vector size (small dummy vector — Qdrant requires vectors, we use a minimal one)
VECTOR_SIZE = 4


def get_qdrant_client() -> QdrantClient:
    """Get or create singleton Qdrant Cloud client"""
    global _qdrant_client
    if _qdrant_client is None:
        _qdrant_client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY,
            timeout=30,
        )
        logger.info(f"✅ Connected to Qdrant Cloud at {settings.QDRANT_URL}")
    return _qdrant_client


def ensure_collections(client: QdrantClient = None):
    """Create required collections if they don't exist"""
    if client is None:
        client = get_qdrant_client()

    existing = [c.name for c in client.get_collections().collections]

    if USERS_COLLECTION not in existing:
        client.create_collection(
            collection_name=USERS_COLLECTION,
            vectors_config=VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE,
            ),
        )
        logger.info(f"✅ Created '{USERS_COLLECTION}' collection in Qdrant Cloud")
    else:
        logger.info(f"ℹ️  Collection '{USERS_COLLECTION}' already exists")
