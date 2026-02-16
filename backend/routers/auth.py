"""
Authentication router for login, logout, and token refresh.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional

from core.security import (
    Token,
    TokenData,
    UserPublic,
    create_tokens,
    decode_token,
    authenticate_user,
    get_current_user,
    DEMO_USERS
)

router = APIRouter()


class LoginRequest(BaseModel):
    username: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


# ============ Auth Endpoints ============

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    OAuth2 compatible login endpoint.
    
    Returns access and refresh tokens on successful authentication.
    """
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return create_tokens(user.id, user.role)


@router.post("/login/json", response_model=Token)
async def login_json(request: LoginRequest):
    """
    JSON-based login endpoint for non-form clients.
    """
    user = authenticate_user(request.username, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    return create_tokens(user.id, user.role)


@router.post("/refresh", response_model=Token)
async def refresh_token(request: RefreshRequest):
    """
    Refresh access token using a valid refresh token.
    """
    token_data = decode_token(request.refresh_token)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    return create_tokens(token_data.user_id, token_data.role)


@router.get("/me", response_model=UserPublic)
async def get_me(current_user: TokenData = Depends(get_current_user)):
    """
    Get the current authenticated user's profile.
    """
    # In production, fetch from database
    for username, user in DEMO_USERS.items():
        if user.id == current_user.user_id:
            return UserPublic(
                id=user.id,
                username=user.username,
                role=user.role,
                email=user.email
            )
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found"
    )


@router.post("/logout")
async def logout(current_user: TokenData = Depends(get_current_user)):
    """
    Logout endpoint (client should discard tokens).
    
    In a production system, you might want to:
    - Add the token to a blacklist
    - Invalidate refresh tokens in the database
    """
    return {"message": "Successfully logged out", "user_id": current_user.user_id}
