from typing import Optional, List, Callable
from fastapi import HTTPException, Request, Response, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
import logging
from datetime import datetime
from .auth0_client import auth0_client
from .cognito_client import cognito_client
from .models import UserRole, UserInfo
from ..config.settings import settings

logger = logging.getLogger(__name__)

# Security scheme for extracting Bearer tokens
security = HTTPBearer(auto_error=False)


def get_auth_client():
    """Get the appropriate auth client (Cognito preferred, Auth0 fallback)."""
    if cognito_client:
        return cognito_client
    elif auth0_client:
        return auth0_client
    else:
        return None


class AuthenticationError(HTTPException):
    """Custom authentication exception."""
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class AuthorizationError(HTTPException):
    """Custom authorization exception."""
    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """Middleware for handling authentication and authorization."""
    
    def __init__(self, app, excluded_paths: Optional[List[str]] = None):
        super().__init__(app)
        self.excluded_paths = excluded_paths or [
            "/docs", "/redoc", "/openapi.json", "/health", "/status",
            "/auth/login", "/auth/callback", "/auth/logout", "/"
        ]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process authentication for incoming requests."""
        
        # Skip authentication for excluded paths
        if any(request.url.path.startswith(path) for path in self.excluded_paths):
            return await call_next(request)
        
        # Skip authentication if disabled
        if not settings.enable_auth:
            return await call_next(request)
        
        # Check if endpoint requires authentication
        if request.url.path not in settings.auth_required_endpoints:
            return await call_next(request)
        
        # Extract and validate token
        try:
            user_info = await self._authenticate_request(request)
            request.state.user = user_info
            logger.info(f"Authenticated user: {user_info.email} ({user_info.role.value})")
        except AuthenticationError as e:
            logger.warning(f"Authentication failed for {request.url.path}: {e.detail}")
            raise e
        
        return await call_next(request)
    
    async def _authenticate_request(self, request: Request) -> UserInfo:
        """Authenticate the request and return user information."""
        
        # Extract token from Authorization header
        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise AuthenticationError("Missing or invalid authorization header")
        
        token = auth_header[7:]  # Remove "Bearer " prefix

        auth_client = get_auth_client()
        if not auth_client:
            raise AuthenticationError("Authentication service not configured")

        try:
            # Verify JWT token
            payload = auth_client.verify_internal_jwt(token)
            
            # Create UserInfo from JWT payload
            user_info = UserInfo(
                user_id=payload["sub"],
                email=payload["email"],
                name=payload.get("name"),
                role=UserRole(payload["role"]),
                institution=payload.get("institution"),
                provider=payload.get("provider", "auth0"),
                last_login=datetime.utcnow()
            )
            
            return user_info
            
        except Exception as e:
            raise AuthenticationError(f"Token validation failed: {str(e)}")


def get_current_user(request: Request) -> Optional[UserInfo]:
    """Get current authenticated user from request state."""
    return getattr(request.state, "user", None)


def require_auth(request: Request) -> UserInfo:
    """Require authentication and return user info."""
    user = get_current_user(request)
    if not user:
        raise AuthenticationError("Authentication required")
    return user


def require_role(request: Request, required_roles: List[UserRole]) -> UserInfo:
    """Require specific role and return user info."""
    user = require_auth(request)
    
    if user.role not in required_roles:
        raise AuthorizationError(
            f"Role '{user.role.value}' not authorized. Required: {[r.value for r in required_roles]}"
        )
    
    return user


def require_admin(request: Request) -> UserInfo:
    """Require admin role."""
    return require_role(request, [UserRole.ADMIN])


def require_educator_or_admin(request: Request) -> UserInfo:
    """Require educator or admin role."""
    return require_role(request, [UserRole.EDUCATOR, UserRole.ADMIN])


class RoleChecker:
    """Dependency for checking user roles."""
    
    def __init__(self, allowed_roles: List[UserRole]):
        self.allowed_roles = allowed_roles
    
    def __call__(self, request: Request) -> UserInfo:
        return require_role(request, self.allowed_roles)


# Common role dependencies
RequireAuth = lambda: require_auth
RequireAdmin = RoleChecker([UserRole.ADMIN])
RequireEducator = RoleChecker([UserRole.EDUCATOR, UserRole.ADMIN])
RequireStudent = RoleChecker([UserRole.STUDENT, UserRole.EDUCATOR, UserRole.ADMIN])


def check_endpoint_permission(endpoint: str, method: str, user_role: UserRole) -> bool:
    """Check if user role has permission for specific endpoint."""
    
    # Define permission matrix
    permissions = {
        # Admin can access everything
        UserRole.ADMIN: ["*"],
        
        # Educators can access most endpoints
        UserRole.EDUCATOR: [
            "/v1/chat/completions",
            "/v1/models",
            "/health",
            "/status",
            "/auth/*"
        ],
        
        # Students have limited access
        UserRole.STUDENT: [
            "/v1/chat/completions",
            "/v1/models", 
            "/health",
            "/auth/*"
        ],
        
        # Guests have minimal access
        UserRole.GUEST: [
            "/health",
            "/auth/*"
        ]
    }
    
    user_permissions = permissions.get(user_role, [])
    
    # Check for wildcard access
    if "*" in user_permissions:
        return True
    
    # Check for exact match or wildcard pattern
    for permission in user_permissions:
        if permission.endswith("/*"):
            if endpoint.startswith(permission[:-2]):
                return True
        elif permission == endpoint:
            return True
    
    return False


async def validate_token_with_provider(token: str) -> dict:
    """Validate token directly with the auth provider (fallback method)."""
    auth_client = get_auth_client()
    if not auth_client:
        raise AuthenticationError("Auth client not configured")

    try:
        # Get JWKS from the provider
        jwks = await auth_client.get_jwks()

        # Validate token against provider JWKS
        # This is a simplified version - production should handle key rotation
        payload = auth_client.verify_internal_jwt(token)
        return payload

    except Exception as e:
        provider_name = "Cognito" if cognito_client else "Auth0" if auth0_client else "Unknown"
        raise AuthenticationError(f"{provider_name} token validation failed: {str(e)}")


class TokenBlacklist:
    """Simple in-memory token blacklist for logged out tokens."""
    
    def __init__(self):
        self._blacklisted_tokens = set()
    
    def blacklist_token(self, token: str):
        """Add token to blacklist."""
        self._blacklisted_tokens.add(token)
    
    def is_blacklisted(self, token: str) -> bool:
        """Check if token is blacklisted."""
        return token in self._blacklisted_tokens
    
    def cleanup_expired_tokens(self):
        """Remove expired tokens from blacklist (should be run periodically)."""
        # In a production system, this would parse JWT exp claims
        # For now, we rely on JWT expiration validation
        pass


# Global token blacklist instance
token_blacklist = TokenBlacklist()