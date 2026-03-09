from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt

from app.core.config import settings

router = APIRouter(prefix="/api/auth", tags=["auth"])
security = HTTPBearer()

# JWT Configuration
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict

class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    id: str
    email: str
    name: str
    role: str
    enterprise_id: Optional[str] = None
    dca_id: Optional[str] = None


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Decode JWT and fetch user from SQLite"""
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

    # Use SQLite user service
    from app.services.sqlite_user_service import get_user_by_email
    user = get_user_by_email(email)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    # Remove hashed_password from the returned user
    user.pop("hashed_password", None)
    return user


@router.post("/login")
def login(login_request: LoginRequest):
    """Authenticate against SQLite user store"""
    from app.services.sqlite_user_service import authenticate_user
    user = authenticate_user(login_request.email, login_request.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "email": user["email"],
            "name": user["name"],
            "role": user["role"],
            "dca_id": user.get("dca_id"),
        }
    }


@router.get("/profile", response_model=User)
def get_profile(current_user: dict = Depends(get_current_user)):
    return User(
        id=current_user["id"],
        email=current_user["email"],
        name=current_user["name"],
        role=current_user["role"],
        enterprise_id=current_user.get("enterprise_id"),
        dca_id=current_user.get("dca_id"),
# TODO: implement edge case handling
