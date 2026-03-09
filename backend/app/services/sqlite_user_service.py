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
    """Create a new user in SQLite"""
    db = _get_db()
    try:
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            raise ValueError(f"User with email '{email}' already exists")

        user = User(
            id=str(uuid.uuid4()),
            email=email,
            hashed_password=_hash_password(password),
            full_name=name,
            role=role,
            dca_id=dca_id,
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"✅ Created user {email} (role={role})")
        return _user_to_dict(user)
    finally:
        db.close()


# ─── READ ──────────────────────────────────────────────────────────────────

def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    db = _get_db()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        return _user_to_dict(user) if user else None
    finally:
        db.close()


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    db = _get_db()
    try:
        user = db.query(User).filter(User.email == email).first()
        if user:
            result = _user_to_dict(user)
            result["hashed_password"] = user.hashed_password
            return result
        return None
    finally:
        db.close()


def get_all_users(skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
    db = _get_db()
    try:
        users = db.query(User).offset(skip).limit(limit).all()
        return [_user_to_dict(u) for u in users]
    finally:
        db.close()


# ─── UPDATE ────────────────────────────────────────────────────────────────

def update_user(user_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    db = _get_db()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None

        if "password" in updates:
            user.hashed_password = _hash_password(updates.pop("password"))
        if "name" in updates:
            user.full_name = updates.pop("name")
        if "email" in updates:
            user.email = updates["email"]
        if "role" in updates:
            user.role = updates["role"]
        if "is_active" in updates:
            user.is_active = updates["is_active"]
        if "dca_id" in updates:
            user.dca_id = updates["dca_id"]

        db.commit()
        db.refresh(user)
        logger.info(f"✅ Updated user {user_id}")
        return _user_to_dict(user)
    finally:
        db.close()


def disable_user(user_id: str) -> Optional[Dict[str, Any]]:
    """Toggle user active status"""
    db = _get_db()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        user.is_active = not user.is_active
        db.commit()
        db.refresh(user)
        logger.info(f"✅ {'Disabled' if not user.is_active else 'Enabled'} user {user.email}")
        return _user_to_dict(user)
    finally:
        db.close()


def reset_password(user_id: str) -> Optional[Dict[str, Any]]:
    """Generate a new random password for a user"""
    db = _get_db()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None

        new_password = _generate_password()
        user.hashed_password = _hash_password(new_password)
        db.commit()
        db.refresh(user)
        logger.info(f"✅ Reset password for {user.email}")
        result = _user_to_dict(user)
        result["new_password"] = new_password
        return result
    finally:
        db.close()


def delete_user(user_id: str) -> bool:
    db = _get_db()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        db.delete(user)
        db.commit()
        return True
    finally:
        db.close()


# ─── AUTH ──────────────────────────────────────────────────────────────────

def authenticate_user(email: str, password: str) -> Optional[Dict[str, Any]]:
    """Authenticate by email + password"""
    user_data = get_user_by_email(email)
    if not user_data:
        return None
    if not _verify_password(password, user_data.get("hashed_password", "")):
        return None
    if not user_data.get("is_active", True):
        return None
    # Remove hashed_password from returned data
    user_data.pop("hashed_password", None)
    return user_data


# ─── HELPERS ───────────────────────────────────────────────────────────────

def _generate_password(length: int = 10) -> str:
    """Generate a strong random password"""
    chars = string.ascii_letters + string.digits + "!@#$"
    # Ensure at least one of each type
    password = [
        random.choice(string.ascii_uppercase),
        random.choice(string.ascii_lowercase),
        random.choice(string.digits),
        random.choice("!@#$"),
    ]
    password += [random.choice(chars) for _ in range(length - 4)]
    random.shuffle(password)
    return "".join(password)


def _generate_email(role: str) -> str:
    """Generate a unique email for a role"""
    suffix = str(random.randint(1000, 9999))
    if role == "enterprise_admin":
        return f"admin{suffix}@rinexor.ai"
    elif role == "dca_agent":
        return f"agent{suffix}@rinexor.ai"
    else:
        return f"user{suffix}@rinexor.ai"


def create_admin_user(role: str) -> Dict[str, Any]:
    """Create a new admin/agent user with auto-generated credentials"""
    email = _generate_email(role)
    password = _generate_password()

    if role == "enterprise_admin":
        name = f"Enterprise Admin ({email.split('@')[0]})"
    elif role == "dca_agent":
        name = f"DCA Agent ({email.split('@')[0]})"
    else:
        name = f"User ({email.split('@')[0]})"

    user = create_user(email=email, password=password, name=name, role=role)
    user["generated_password"] = password
    return user


# ─── SEED DEFAULTS ─────────────────────────────────────────────────────────

def seed_default_users():
    """Seed default users if they don't exist"""
    defaults = [
        {
            "email": "superadmin@rinexor.ai",
            "password": "Super@123",
            "name": "System Administrator",
            "role": "super_admin",
        },
        {
            "email": "admin@enterprise.com",
            "password": "Enterprise@123",
            "name": "John Doe",
            "role": "enterprise_admin",
        },
        {
            "email": "agent@dca.com",
            "password": "DCA@123",
            "name": "Agent Smith",
            "role": "dca_agent",
        },
    ]

    count = 0
    for u in defaults:
        existing = get_user_by_email(u["email"])
        if not existing:
            try:
                create_user(
                    email=u["email"],
                    password=u["password"],
                    name=u["name"],
                    role=u["role"],
                )
                count += 1
            except ValueError:
                pass
    if count:
        logger.info(f"✅ Seeded {count} default users")
    return count
