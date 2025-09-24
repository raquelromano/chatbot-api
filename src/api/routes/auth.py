from typing import Optional
from fastapi import APIRouter, Request, Response, HTTPException, Depends, status, Query
from fastapi.responses import RedirectResponse, JSONResponse
from pydantic import BaseModel, Field
import secrets
import logging
from urllib.parse import urlencode
from datetime import datetime

from ...auth.auth0_client import auth0_client
from ...auth.cognito_client import cognito_client
from ...auth.middleware import (
    get_current_user, require_auth, token_blacklist,
    AuthenticationError, AuthorizationError
)
from ...auth.models import (
    LoginRequest, LoginResponse, TokenRequest, TokenResponse,
    UserInfo, UserRole, LogoutRequest, RefreshTokenRequest,
    AuthError, InstitutionConfig
)
from ...config.settings import settings

logger = logging.getLogger(__name__)
router = APIRouter(tags=["authentication"])


def get_auth_client():
    """Get the appropriate auth client (Cognito preferred, Auth0 fallback)."""
    if cognito_client:
        return cognito_client
    elif auth0_client:
        return auth0_client
    else:
        return None


class OnboardingRequest(BaseModel):
    """Request model for user onboarding/role selection."""
    role: UserRole = Field(..., description="Selected user role")
    institution_id: Optional[str] = Field(None, description="Institution ID if applicable")


class OnboardingResponse(BaseModel):
    """Response model for successful onboarding."""
    user: UserInfo = Field(..., description="Updated user information")
    access_token: str = Field(..., description="New JWT token with updated info")


class UserProfileResponse(BaseModel):
    """Response model for user profile."""
    user: UserInfo = Field(..., description="User information")
    institution: Optional[InstitutionConfig] = Field(None, description="Institution details if applicable")


@router.get("/login", response_model=LoginResponse)
async def login(
    redirect_uri: str = Query(..., description="Redirect URI after authentication"),
    connection: Optional[str] = Query(None, description="Specific provider connection"),
    state: Optional[str] = Query(None, description="State parameter for CSRF protection")
):
    """Initiate OAuth login flow."""
    auth_client = get_auth_client()
    if not auth_client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service not configured"
        )

    try:
        login_response = auth_client.generate_auth_url(
            redirect_uri=redirect_uri,
            connection=connection,
            state=state
        )

        logger.info(f"Generated login URL for redirect_uri: {redirect_uri}")
        return login_response

    except Exception as e:
        logger.error(f"Login initiation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login initiation failed: {str(e)}"
        )


@router.get("/callback")
async def auth_callback(
    code: str = Query(..., description="Authorization code from provider"),
    state: str = Query(..., description="State parameter for verification"),
    redirect_uri: str = Query(..., description="Original redirect URI"),
    error: Optional[str] = Query(None, description="Error code if authentication failed"),
    error_description: Optional[str] = Query(None, description="Error description")
):
    """Handle OAuth callback and exchange code for tokens."""
    auth_client = get_auth_client()
    if not auth_client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service not configured"
        )
    
    # Handle authentication errors
    if error:
        logger.warning(f"Auth callback error: {error} - {error_description}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=AuthError(
                error=error,
                error_description=error_description or "Authentication failed"
            ).dict()
        )
    
    try:
        # Exchange code for token
        token_response = await auth_client.exchange_code_for_token(code, redirect_uri)

        # Get user info
        user_info = await auth_client.get_user_info(token_response.access_token)

        # Create internal JWT
        internal_jwt = auth_client.create_internal_jwt(user_info)
        
        logger.info(f"User authenticated: {user_info.email}")
        
        # Return token response with user info
        return JSONResponse(content={
            "access_token": internal_jwt,
            "token_type": "Bearer",
            "expires_in": settings.jwt_expiration_hours * 3600,
            "user": user_info.dict(),
            "requires_onboarding": user_info.role == UserRole.GUEST
        })
        
    except Exception as e:
        logger.error(f"Auth callback failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication failed: {str(e)}"
        )


@router.post("/onboarding", response_model=OnboardingResponse)
async def complete_onboarding(
    request: OnboardingRequest,
    current_user: UserInfo = Depends(require_auth)
):
    """Complete user onboarding by setting role and institution."""
    auth_client = get_auth_client()
    if not auth_client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service not configured"
        )
    
    try:
        # Validate institution if provided
        if request.institution_id:
            institution = auth_client.get_institution_by_id(request.institution_id)
            if not institution or not institution.enabled:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid or disabled institution: {request.institution_id}"
                )
        
        # Update user info
        updated_user = current_user.copy(update={
            "role": request.role,
            "institution": request.institution_id,
            "last_login": datetime.utcnow()
        })
        
        # Create new JWT with updated info
        new_jwt = auth_client.create_internal_jwt(updated_user)
        
        logger.info(f"User onboarding completed: {updated_user.email} -> {request.role.value}")
        
        return OnboardingResponse(
            user=updated_user,
            access_token=new_jwt
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Onboarding failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Onboarding failed: {str(e)}"
        )


@router.get("/profile", response_model=UserProfileResponse)
async def get_user_profile(current_user: UserInfo = Depends(require_auth)):
    """Get current user profile."""
    auth_client = get_auth_client()
    if not auth_client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service not configured"
        )
    
    try:
        # Get institution details if user has one
        institution = None
        if current_user.institution:
            institution = auth_client.get_institution_by_id(current_user.institution)
        
        return UserProfileResponse(
            user=current_user,
            institution=institution
        )
        
    except Exception as e:
        logger.error(f"Profile retrieval failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Profile retrieval failed: {str(e)}"
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(
    request: RefreshTokenRequest,
    current_user: UserInfo = Depends(require_auth)
):
    """Refresh access token using refresh token."""
    auth_client = get_auth_client()
    if not auth_client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service not configured"
        )
    
    try:
        # For simplicity, we'll just create a new internal JWT
        # In production, you might want to validate the refresh token with the provider
        new_jwt = auth_client.create_internal_jwt(current_user)
        
        return TokenResponse(
            access_token=new_jwt,
            token_type="Bearer",
            expires_in=settings.jwt_expiration_hours * 3600
        )
        
    except Exception as e:
        logger.error(f"Token refresh failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Token refresh failed: {str(e)}"
        )


@router.post("/logout")
async def logout(
    request: Request,
    logout_request: LogoutRequest,
    current_user: UserInfo = Depends(require_auth)
):
    """Logout user and invalidate tokens."""
    auth_client = get_auth_client()
    if not auth_client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service not configured"
        )
    
    try:
        # Get token from request
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            # Add token to blacklist
            token_blacklist.blacklist_token(token)
        
        # Generate logout URL
        logout_url = auth_client.generate_logout_url(logout_request.redirect_uri)
        
        logger.info(f"User logged out: {current_user.email}")
        
        return JSONResponse(content={
            "message": "Logout successful",
            "logout_url": logout_url
        })
        
    except Exception as e:
        logger.error(f"Logout failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Logout failed: {str(e)}"
        )


@router.get("/institutions")
async def list_institutions():
    """List available institutions for registration."""
    auth_client = get_auth_client()
    if not auth_client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service not configured"
        )
    
    try:
        # Filter only enabled institutions and remove sensitive config
        public_institutions = []
        for institution in auth_client.institutions.values():
            if institution.enabled:
                public_institutions.append({
                    "institution_id": institution.institution_id,
                    "name": institution.name,
                    "domain": institution.domain,
                    "logo_url": institution.logo_url,
                    "primary_color": institution.primary_color
                })
        
        return {"institutions": public_institutions}
        
    except Exception as e:
        logger.error(f"Institution listing failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Institution listing failed: {str(e)}"
        )


@router.get("/status")
async def auth_status():
    """Get authentication service status."""
    return {
        "auth_enabled": settings.enable_auth,
        "auth_configured": get_auth_client() is not None,
        "auth_provider": "cognito" if cognito_client else "auth0" if auth0_client else None,
        "protected_endpoints": settings.auth_required_endpoints
    }