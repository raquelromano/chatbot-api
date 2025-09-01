from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from enum import Enum


class AuthProvider(str, Enum):
    """Supported authentication providers."""
    GOOGLE = "google"
    MICROSOFT = "microsoft"  
    SAML = "saml"
    GITHUB = "github"
    AUTH0 = "auth0"


class UserRole(str, Enum):
    """User roles for authorization."""
    STUDENT = "student"
    EDUCATOR = "educator"
    ADMIN = "admin"
    GUEST = "guest"


class LoginRequest(BaseModel):
    """Request model for user login."""
    provider: AuthProvider = Field(..., description="Authentication provider to use")
    redirect_uri: Optional[str] = Field(None, description="Redirect URI after successful login")
    state: Optional[str] = Field(None, description="State parameter for CSRF protection")
    connection: Optional[str] = Field(None, description="Specific connection for Auth0 (e.g., 'google-oauth2', 'saml-institution')")


class LoginResponse(BaseModel):
    """Response model for login initiation."""
    auth_url: str = Field(..., description="URL to redirect user for authentication")
    state: str = Field(..., description="State parameter for verification")


class TokenRequest(BaseModel):
    """Request model for token exchange."""
    code: str = Field(..., description="Authorization code from provider")
    state: str = Field(..., description="State parameter for verification")


class TokenResponse(BaseModel):
    """Response model containing authentication tokens."""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: Optional[str] = Field(None, description="Refresh token")
    token_type: str = Field(default="Bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")


class UserInfo(BaseModel):
    """User information model."""
    user_id: str = Field(..., description="Unique user identifier")
    email: str = Field(..., description="User email address")
    name: Optional[str] = Field(None, description="User display name")
    picture: Optional[str] = Field(None, description="User profile picture URL")
    provider: AuthProvider = Field(..., description="Authentication provider used")
    role: UserRole = Field(default=UserRole.STUDENT, description="User role")
    institution: Optional[str] = Field(None, description="Educational institution")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Account creation timestamp")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional user metadata")


class SessionInfo(BaseModel):
    """Session information model."""
    session_id: str = Field(..., description="Unique session identifier")
    user_id: str = Field(..., description="User ID associated with session")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Session creation timestamp")
    expires_at: datetime = Field(..., description="Session expiration timestamp")
    last_activity: datetime = Field(default_factory=datetime.utcnow, description="Last activity timestamp")
    ip_address: Optional[str] = Field(None, description="User IP address")
    user_agent: Optional[str] = Field(None, description="User agent string")


class AuthError(BaseModel):
    """Authentication error model."""
    error: str = Field(..., description="Error code")
    error_description: str = Field(..., description="Human-readable error description")
    error_uri: Optional[str] = Field(None, description="URI with error information")


class RefreshTokenRequest(BaseModel):
    """Request model for token refresh."""
    refresh_token: str = Field(..., description="Valid refresh token")


class LogoutRequest(BaseModel):
    """Request model for user logout."""
    redirect_uri: Optional[str] = Field(None, description="Redirect URI after logout")


class InstitutionConfig(BaseModel):
    """Configuration for educational institutions."""
    institution_id: str = Field(..., description="Unique institution identifier")
    name: str = Field(..., description="Institution name")
    domain: str = Field(..., description="Institution email domain")
    auth_provider: AuthProvider = Field(..., description="Preferred authentication provider")
    saml_config: Optional[Dict[str, Any]] = Field(None, description="SAML configuration if applicable")
    oidc_config: Optional[Dict[str, Any]] = Field(None, description="OIDC configuration if applicable")
    logo_url: Optional[str] = Field(None, description="Institution logo URL")
    primary_color: Optional[str] = Field(None, description="Institution brand color")
    enabled: bool = Field(default=True, description="Whether institution is active")


class PermissionCheck(BaseModel):
    """Model for checking user permissions."""
    endpoint: str = Field(..., description="API endpoint being accessed")
    method: str = Field(..., description="HTTP method")
    user_role: UserRole = Field(..., description="User role")
    required_roles: List[UserRole] = Field(..., description="Required roles for access")
    allowed: bool = Field(..., description="Whether access is allowed")