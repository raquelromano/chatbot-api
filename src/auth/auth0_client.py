import os
import secrets
import urllib.parse
from typing import Dict, Optional, Any
import httpx
from jose import jwt, JWTError
from datetime import datetime, timedelta
from ..config.settings import settings
from .models import (
    AuthProvider, UserRole, InstitutionConfig, UserInfo, 
    LoginResponse, TokenResponse, AuthError
)


class Auth0Client:
    """Auth0 client for handling OAuth flows and user authentication."""
    
    def __init__(self):
        self.domain = settings.auth0_domain
        self.client_id = settings.auth0_client_id
        self.client_secret = settings.auth0_client_secret
        self.audience = settings.auth0_audience
        
        if not all([self.domain, self.client_id, self.client_secret]):
            raise ValueError("Auth0 configuration missing. Set AUTH0_DOMAIN, AUTH0_CLIENT_ID, and AUTH0_CLIENT_SECRET")
        
        self.base_url = f"https://{self.domain}"
        self.jwks_url = f"{self.base_url}/.well-known/jwks.json"
        
        # Institution registry for pilot phase
        self.institutions = self._load_institution_registry()
    
    def _load_institution_registry(self) -> Dict[str, InstitutionConfig]:
        """Load the institution registry for the pilot phase."""
        return {
            "example.edu": InstitutionConfig(
                institution_id="example",
                name="Example University",
                domain="example.edu",
                auth_provider=AuthProvider.GOOGLE,
                logo_url="https://example.edu/logo.png",
                primary_color="#003366",
                enabled=True
            ),
            "testcollege.edu": InstitutionConfig(
                institution_id="testcollege",
                name="Test College",
                domain="testcollege.edu",
                auth_provider=AuthProvider.MICROSOFT,
                logo_url="https://testcollege.edu/assets/logo.png",
                primary_color="#8B0000",
                enabled=True
            ),
            "demo-school.org": InstitutionConfig(
                institution_id="demoschool",
                name="Demo School",
                domain="demo-school.org",
                auth_provider=AuthProvider.SAML,
                saml_config={
                    "sso_url": "https://demo-school.org/saml/sso",
                    "certificate": "-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----"
                },
                logo_url="https://demo-school.org/logo.svg",
                primary_color="#2E8B57",
                enabled=True
            )
        }
    
    def get_institution_by_domain(self, email_domain: str) -> Optional[InstitutionConfig]:
        """Get institution configuration by email domain."""
        return self.institutions.get(email_domain.lower())
    
    def get_institution_by_id(self, institution_id: str) -> Optional[InstitutionConfig]:
        """Get institution configuration by ID."""
        for institution in self.institutions.values():
            if institution.institution_id == institution_id:
                return institution
        return None
    
    def generate_auth_url(self, 
                         redirect_uri: str, 
                         connection: Optional[str] = None,
                         state: Optional[str] = None) -> LoginResponse:
        """Generate Auth0 authorization URL."""
        if not state:
            state = secrets.token_urlsafe(32)
        
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "scope": "openid profile email",
            "state": state
        }
        
        if connection:
            params["connection"] = connection
        
        if self.audience:
            params["audience"] = self.audience
        
        auth_url = f"{self.base_url}/authorize?" + urllib.parse.urlencode(params)
        
        return LoginResponse(auth_url=auth_url, state=state)
    
    async def exchange_code_for_token(self, code: str, redirect_uri: str) -> TokenResponse:
        """Exchange authorization code for access token."""
        token_data = {
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "redirect_uri": redirect_uri
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/oauth/token",
                data=token_data,
                headers={"content-type": "application/x-www-form-urlencoded"}
            )
        
        if response.status_code != 200:
            error_data = response.json()
            raise Exception(f"Token exchange failed: {error_data}")
        
        token_response = response.json()
        return TokenResponse(**token_response)
    
    async def get_user_info(self, access_token: str) -> UserInfo:
        """Get user information from Auth0."""
        headers = {"Authorization": f"Bearer {access_token}"}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/userinfo",
                headers=headers
            )
        
        if response.status_code != 200:
            raise Exception(f"Failed to get user info: {response.status_code}")
        
        user_data = response.json()
        
        # Extract email domain and check for institutional affiliation
        email = user_data.get("email", "")
        email_domain = email.split("@")[-1] if "@" in email else ""
        institution = self.get_institution_by_domain(email_domain)
        
        # Determine default role based on institution
        default_role = UserRole.STUDENT if institution else UserRole.GUEST
        
        return UserInfo(
            user_id=user_data["sub"],
            email=email,
            name=user_data.get("name"),
            picture=user_data.get("picture"),
            provider=self._determine_provider(user_data.get("sub", "")),
            role=default_role,
            institution=institution.institution_id if institution else None,
            metadata={
                "auth0_user_id": user_data["sub"],
                "email_verified": user_data.get("email_verified", False),
                "locale": user_data.get("locale"),
                "updated_at": user_data.get("updated_at")
            }
        )
    
    def _determine_provider(self, auth0_user_id: str) -> AuthProvider:
        """Determine auth provider from Auth0 user ID format."""
        if auth0_user_id.startswith("google-oauth2|"):
            return AuthProvider.GOOGLE
        elif auth0_user_id.startswith("windowslive|") or auth0_user_id.startswith("azure-ad|"):
            return AuthProvider.MICROSOFT
        elif auth0_user_id.startswith("github|"):
            return AuthProvider.GITHUB
        elif auth0_user_id.startswith("samlp|"):
            return AuthProvider.SAML
        else:
            return AuthProvider.AUTH0
    
    async def refresh_token(self, refresh_token: str) -> TokenResponse:
        """Refresh access token using refresh token."""
        token_data = {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": refresh_token
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/oauth/token",
                data=token_data,
                headers={"content-type": "application/x-www-form-urlencoded"}
            )
        
        if response.status_code != 200:
            error_data = response.json()
            raise Exception(f"Token refresh failed: {error_data}")
        
        token_response = response.json()
        return TokenResponse(**token_response)
    
    def generate_logout_url(self, redirect_uri: Optional[str] = None) -> str:
        """Generate Auth0 logout URL."""
        params = {"client_id": self.client_id}
        if redirect_uri:
            params["returnTo"] = redirect_uri
        
        return f"{self.base_url}/v2/logout?" + urllib.parse.urlencode(params)
    
    async def get_jwks(self) -> Dict[str, Any]:
        """Get JSON Web Key Set from Auth0."""
        async with httpx.AsyncClient() as client:
            response = await client.get(self.jwks_url)
        
        if response.status_code != 200:
            raise Exception(f"Failed to get JWKS: {response.status_code}")
        
        return response.json()
    
    def create_internal_jwt(self, user_info: UserInfo) -> str:
        """Create internal JWT token for the user session."""
        now = datetime.utcnow()
        expiration = now + timedelta(hours=settings.jwt_expiration_hours)
        
        payload = {
            "sub": user_info.user_id,
            "email": user_info.email,
            "name": user_info.name,
            "role": user_info.role.value,
            "institution": user_info.institution,
            "provider": user_info.provider.value,
            "iat": now.timestamp(),
            "exp": expiration.timestamp(),
            "iss": "chatbot-wrapper-demo",
            "aud": "chatbot-api"
        }
        
        return jwt.encode(
            payload, 
            settings.jwt_secret_key, 
            algorithm=settings.jwt_algorithm
        )
    
    def verify_internal_jwt(self, token: str) -> Dict[str, Any]:
        """Verify and decode internal JWT token."""
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret_key,
                algorithms=[settings.jwt_algorithm],
                audience="chatbot-api",
                issuer="chatbot-wrapper-demo"
            )
            return payload
        except JWTError as e:
            raise Exception(f"Invalid JWT token: {str(e)}")


# Global Auth0 client instance
auth0_client = Auth0Client() if all([settings.auth0_domain, settings.auth0_client_id, settings.auth0_client_secret]) else None