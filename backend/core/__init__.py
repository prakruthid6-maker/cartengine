"""
Core module for backend configuration and shared utilities.
"""

from .security import (
    Token,
    TokenData,
    UserInDB,
    UserPublic,
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    create_tokens,
    decode_token,
    get_current_user,
    get_current_active_user,
    require_role,
    require_admin,
    authenticate_user,
    oauth2_scheme,
)

__all__ = [
    "Token",
    "TokenData",
    "UserInDB",
    "UserPublic",
    "verify_password",
    "get_password_hash",
    "create_access_token",
    "create_refresh_token",
    "create_tokens",
    "decode_token",
    "get_current_user",
    "get_current_active_user",
    "require_role",
    "require_admin",
    "authenticate_user",
    "oauth2_scheme",
]
