"""AWS Cognito client for handling OAuth flows and user authentication."""

import os
import secrets
import urllib.parse
from typing import Dict, Optional, Any
import boto3
from botocore.exceptions import ClientError
from jose import jwt, JWTError
from datetime import datetime, timedelta
import httpx
from ..config.settings import settings
from .models import (
    AuthProvider, UserRole, InstitutionConfig, UserInfo,
    LoginResponse, TokenResponse, AuthError
)


class CognitoClient:
    """AWS Cognito client for handling OAuth flows and user authentication."""

    def __init__(self):
        self.user_pool_id = settings.cognito_user_pool_id
        self.client_id = settings.cognito_client_id
        self.region = settings.cognito_region or "us-east-1"

        if not all([self.user_pool_id, self.client_id]):
            raise ValueError("Cognito configuration missing. Set COGNITO_USER_POOL_ID and COGNITO_CLIENT_ID")

        # Initialize Cognito client
        self.cognito_client = boto3.client('cognito-idp', region_name=self.region)

        # Cognito URLs
        self.cognito_domain = f"https://chatbot-api-{settings.aws_account_id}.auth.{self.region}.amazoncognito.com"
        self.jwks_url = f"https://cognito-idp.{self.region}.amazonaws.com/{self.user_pool_id}/.well-known/jwks.json"
        self.issuer = f"https://cognito-idp.{self.region}.amazonaws.com/{self.user_pool_id}"

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
        """Generate Cognito Hosted UI authorization URL."""
        if not state:
            state = secrets.token_urlsafe(32)

        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "scope": "openid email profile",
            "state": state
        }

        # Map connection to Cognito identity provider
        if connection:
            provider_map = {
                "google-oauth2": "Google",
                "windowslive": "LoginWithAmazon",  # Or configure Microsoft
                "github": "SignInWithApple",  # Or configure GitHub
            }
            if connection in provider_map:
                params["identity_provider"] = provider_map[connection]

        auth_url = f"{self.cognito_domain}/oauth2/authorize?" + urllib.parse.urlencode(params)

        return LoginResponse(auth_url=auth_url, state=state)

    async def exchange_code_for_token(self, code: str, redirect_uri: str) -> TokenResponse:
        """Exchange authorization code for access token."""
        token_data = {
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "code": code,
            "redirect_uri": redirect_uri
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.cognito_domain}/oauth2/token",
                data=token_data,
                headers={
                    "content-type": "application/x-www-form-urlencoded"
                }
            )

        if response.status_code != 200:
            error_data = response.json()
            raise Exception(f"Token exchange failed: {error_data}")

        token_response = response.json()
        return TokenResponse(**token_response)

    async def get_user_info(self, access_token: str) -> UserInfo:
        """Get user information from Cognito."""
        headers = {"Authorization": f"Bearer {access_token}"}

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.cognito_domain}/oauth2/userInfo",
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
            name=user_data.get("name") or user_data.get("given_name", "") + " " + user_data.get("family_name", ""),
            picture=user_data.get("picture"),
            provider=self._determine_provider_from_token(access_token),
            role=default_role,
            institution=institution.institution_id if institution else None,
            metadata={
                "cognito_user_id": user_data["sub"],
                "email_verified": user_data.get("email_verified", False),
                "locale": user_data.get("locale"),
                "updated_at": user_data.get("updated_at")
            }
        )

    def _determine_provider_from_token(self, access_token: str) -> AuthProvider:
        """Determine auth provider from Cognito token claims."""
        try:
            # Decode token without verification to read claims
            unverified_payload = jwt.get_unverified_claims(access_token)
            identity_providers = unverified_payload.get("identities", [])

            if identity_providers:
                provider_id = identity_providers[0].get("providerName", "").lower()
                if "google" in provider_id:
                    return AuthProvider.GOOGLE
                elif "facebook" in provider_id:
                    return AuthProvider.MICROSOFT  # Or create FACEBOOK enum
                elif "loginwithamazon" in provider_id:
                    return AuthProvider.MICROSOFT
                elif "signinwithapple" in provider_id:
                    return AuthProvider.GITHUB  # Or create APPLE enum

            return AuthProvider.AUTH0  # Default to AUTH0 (representing Cognito)
        except:
            return AuthProvider.AUTH0

    async def refresh_token(self, refresh_token: str) -> TokenResponse:
        """Refresh access token using refresh token."""
        token_data = {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "refresh_token": refresh_token
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.cognito_domain}/oauth2/token",
                data=token_data,
                headers={"content-type": "application/x-www-form-urlencoded"}
            )

        if response.status_code != 200:
            error_data = response.json()
            raise Exception(f"Token refresh failed: {error_data}")

        token_response = response.json()
        return TokenResponse(**token_response)

    def generate_logout_url(self, redirect_uri: Optional[str] = None) -> str:
        """Generate Cognito logout URL."""
        params = {"client_id": self.client_id}
        if redirect_uri:
            params["logout_uri"] = redirect_uri

        return f"{self.cognito_domain}/logout?" + urllib.parse.urlencode(params)

    async def get_jwks(self) -> Dict[str, Any]:
        """Get JSON Web Key Set from Cognito."""
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

    def verify_cognito_jwt(self, token: str) -> Dict[str, Any]:
        """Verify JWT token issued by Cognito."""
        try:
            # Get the token header to find the key ID
            unverified_header = jwt.get_unverified_header(token)
            kid = unverified_header.get("kid")

            if not kid:
                raise Exception("Token missing 'kid' in header")

            # Get JWKS and find the matching key
            # Note: In production, you should cache JWKS
            import asyncio
            jwks = asyncio.run(self.get_jwks())

            key = None
            for k in jwks.get("keys", []):
                if k.get("kid") == kid:
                    key = k
                    break

            if not key:
                raise Exception(f"Unable to find matching key for kid: {kid}")

            # Verify and decode the token
            payload = jwt.decode(
                token,
                key,
                algorithms=["RS256"],
                audience=self.client_id,
                issuer=self.issuer
            )
            return payload
        except JWTError as e:
            raise Exception(f"Invalid Cognito JWT token: {str(e)}")

    async def create_user(self, email: str, temporary_password: str,
                         attributes: Dict[str, str] = None) -> Dict[str, Any]:
        """Create a new user in Cognito User Pool."""
        user_attributes = [
            {"Name": "email", "Value": email},
            {"Name": "email_verified", "Value": "true"}
        ]

        if attributes:
            for key, value in attributes.items():
                user_attributes.append({"Name": key, "Value": value})

        try:
            response = self.cognito_client.admin_create_user(
                UserPoolId=self.user_pool_id,
                Username=email,
                UserAttributes=user_attributes,
                TemporaryPassword=temporary_password,
                MessageAction="SUPPRESS"  # Don't send welcome email
            )
            return response
        except ClientError as e:
            raise Exception(f"Failed to create user: {e.response['Error']['Message']}")

    async def delete_user(self, username: str) -> None:
        """Delete a user from Cognito User Pool."""
        try:
            self.cognito_client.admin_delete_user(
                UserPoolId=self.user_pool_id,
                Username=username
            )
        except ClientError as e:
            raise Exception(f"Failed to delete user: {e.response['Error']['Message']}")

    async def update_user_attributes(self, username: str,
                                   attributes: Dict[str, str]) -> None:
        """Update user attributes in Cognito User Pool."""
        user_attributes = []
        for key, value in attributes.items():
            user_attributes.append({"Name": key, "Value": value})

        try:
            self.cognito_client.admin_update_user_attributes(
                UserPoolId=self.user_pool_id,
                Username=username,
                UserAttributes=user_attributes
            )
        except ClientError as e:
            raise Exception(f"Failed to update user attributes: {e.response['Error']['Message']}")

    async def send_passwordless_auth(self, email: str) -> Dict[str, Any]:
        """Initiate passwordless authentication by sending a code to email."""
        try:
            response = self.cognito_client.admin_initiate_auth(
                UserPoolId=self.user_pool_id,
                ClientId=self.client_id,
                AuthFlow='CUSTOM_AUTH',
                AuthParameters={
                    'USERNAME': email,
                }
            )
            return response
        except ClientError as e:
            if e.response['Error']['Code'] == 'UserNotFoundException':
                # Auto-create user if they don't exist
                await self.create_passwordless_user(email)
                # Retry auth initiation
                response = self.cognito_client.admin_initiate_auth(
                    UserPoolId=self.user_pool_id,
                    ClientId=self.client_id,
                    AuthFlow='CUSTOM_AUTH',
                    AuthParameters={
                        'USERNAME': email,
                    }
                )
                return response
            raise Exception(f"Failed to initiate passwordless auth: {e.response['Error']['Message']}")

    async def verify_passwordless_code(self, email: str, session: str, code: str) -> TokenResponse:
        """Verify the passwordless authentication code."""
        try:
            response = self.cognito_client.admin_respond_to_auth_challenge(
                UserPoolId=self.user_pool_id,
                ClientId=self.client_id,
                ChallengeName='CUSTOM_CHALLENGE',
                ChallengeResponses={
                    'USERNAME': email,
                    'ANSWER': code,
                },
                Session=session
            )

            if 'AuthenticationResult' in response:
                auth_result = response['AuthenticationResult']
                return TokenResponse(
                    access_token=auth_result['AccessToken'],
                    token_type='Bearer',
                    expires_in=auth_result.get('ExpiresIn', 3600),
                    refresh_token=auth_result.get('RefreshToken'),
                    id_token=auth_result.get('IdToken')
                )
            else:
                raise Exception("Authentication failed - no result returned")

        except ClientError as e:
            raise Exception(f"Failed to verify passwordless code: {e.response['Error']['Message']}")

    async def create_passwordless_user(self, email: str) -> Dict[str, Any]:
        """Create a new user for passwordless authentication."""
        try:
            response = self.cognito_client.admin_create_user(
                UserPoolId=self.user_pool_id,
                Username=email,
                UserAttributes=[
                    {"Name": "email", "Value": email},
                    {"Name": "email_verified", "Value": "true"}
                ],
                MessageAction="SUPPRESS",  # Don't send welcome email
                TemporaryPassword=secrets.token_urlsafe(16)  # Random temp password (unused)
            )

            # Set permanent password to bypass temporary password requirement
            self.cognito_client.admin_set_user_password(
                UserPoolId=self.user_pool_id,
                Username=email,
                Password=secrets.token_urlsafe(32),  # Random permanent password (unused)
                Permanent=True
            )

            return response
        except ClientError as e:
            raise Exception(f"Failed to create passwordless user: {e.response['Error']['Message']}")


# Global Cognito client instance
cognito_client = CognitoClient() if all([settings.cognito_user_pool_id, settings.cognito_client_id]) else None