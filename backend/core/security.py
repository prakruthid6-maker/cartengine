"""
Security module for JWT authentication and password hashing.

Provides:
- JWT access and refresh token creation/validation
- Password hashing with bcrypt
- Current user dependency for FastAPI
"""

import os
from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

# Configuration
SECRET_KEY = os.getenv("JWT_SECRET", "your-super-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# ============ Token Models ============

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[str] = None
    role: Optional[str] = None


class UserInDB(BaseModel):
    id: str
    username: str
    hashed_password: str
    role: str = "customer"
    email: Optional[str] = None


class UserPublic(BaseModel):
    id: str
    username: str
    role: str
    email: Optional[str] = None


# ============ Password Functions ============

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


# ============ Token Functions ============

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({
        "exp": expire,
        "type": "access",
        "iat": datetime.utcnow()
    })
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict) -> str:
    """Create a JWT refresh token (longer lived)."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({
        "exp": expire,
        "type": "refresh",
        "iat": datetime.utcnow()
    })
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_tokens(user_id: str, role: str) -> Token:
    """Create both access and refresh tokens for a user."""
    token_data = {"sub": user_id, "role": role}
    return Token(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data)
    )


def decode_token(token: str) -> Optional[TokenData]:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        role: str = payload.get("role", "customer")
        if user_id is None:
            return None
        return TokenData(user_id=user_id, role=role)
    except JWTError:
        return None


# ============ FastAPI Dependencies ============

async def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    """
    Dependency to get the current authenticated user from JWT token.
    Raises HTTPException if token is invalid.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    
    token_data = decode_token(token)
    if token_data is None:
        raise credentials_exception
    
    return token_data


async def get_current_active_user(current_user: TokenData = Depends(get_current_user)) -> TokenData:
    """Dependency that ensures the user is active."""
    # In a real app, you'd check against the database here
    return current_user


def require_role(required_role: str):
    """
    Dependency factory to require a specific role.
    
    Usage:
        @router.get("/admin-only")
        async def admin_route(user: TokenData = Depends(require_role("admin"))):
            ...
    """
    async def role_checker(current_user: TokenData = Depends(get_current_user)) -> TokenData:
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {required_role}"
            )
        return current_user
    return role_checker


# Admin dependency shortcut
require_admin = require_role("admin")


# ============ Demo Users (Replace with DB in production) ============

# Pre-computed bcrypt hashes (generated with get_password_hash)
# user123 -> $2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.StVfhdLOvQlMUe
# admin123 -> $2b$12$eUzivKQVFyMPsYCh5dC3P.IQVNy.sE8c6qHcDMxZ0PZ.uE4./xXvy

DEMO_USERS = {
    "user": UserInDB(
        id="user-001",
        username="user",
        hashed_password="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.StVfhdLOvQlMUe",
        role="customer"
    ),
    "admin": UserInDB(
        id="admin-001",
        username="admin",
        hashed_password="$2b$12$eUzivKQVFyMPsYCh5dC3P.IQVNy.sE8c6qHcDMxZ0PZ.uE4./xXvy",
        role="admin"
    )
}


def authenticate_user(username: str, password: str) -> Optional[UserInDB]:
    """Authenticate a user with username and password."""
    user = DEMO_USERS.get(username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

