"""Authentication module for the chatbot API."""

from .models import (
    AuthProvider,
    UserRole,
    LoginRequest,
    LoginResponse,
    TokenRequest,
    TokenResponse,
    UserInfo,
    SessionInfo,
    AuthError,
    RefreshTokenRequest,
    LogoutRequest,
    InstitutionConfig,
    PermissionCheck,
)
from .auth0_client import auth0_client
from .middleware import (
    AuthenticationMiddleware,
    get_current_user,
    require_auth,
    require_role,
    require_admin,
    require_educator_or_admin,
    RequireAuth,
    RequireAdmin,
    RequireEducator,
    RequireStudent,
)
from .user_manager import user_manager

__all__ = [
    # Models
    "AuthProvider",
    "UserRole", 
    "LoginRequest",
    "LoginResponse",
    "TokenRequest", 
    "TokenResponse",
    "UserInfo",
    "SessionInfo",
    "AuthError",
    "RefreshTokenRequest",
    "LogoutRequest",
    "InstitutionConfig", 
    "PermissionCheck",
    # Auth0 client
    "auth0_client",
    # Middleware and dependencies
    "AuthenticationMiddleware",
    "get_current_user",
    "require_auth",
    "require_role", 
    "require_admin",
    "require_educator_or_admin",
    "RequireAuth",
    "RequireAdmin",
    "RequireEducator", 
    "RequireStudent",
    # User manager
    "user_manager",
]