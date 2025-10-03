from fastapi import APIRouter, Depends, HTTPException
from src.core.oauth2_server import OAuth2AuthorizationServer
from src.core.token_validator import TokenValidator
from src.database.repositories import UserRepository, TokenRepository
from src.api.models import (
    GrantRequest, TokenResponse, TokenRevokeRequest, 
    RevocationResponse, GlobalLogoutRequest, LogoutResponse,
    UserCreate, UserResponse
)
from uuid import UUID

router = APIRouter(prefix="/v1", tags=["auth"])

@router.post("/token", response_model=TokenResponse)
async def issue_token(grant_request: GrantRequest) -> TokenResponse:
    """OAuth 2.0 Token Endpoint
    Supported grant_types: authorization_code, refresh_token, client_credentials
    """
    oauth_server = OAuth2AuthorizationServer()
    return await oauth_server.issue_access_token(grant_request)

@router.get("/tokens/{tenant_id}/{app_id}", response_model=TokenResponse)
async def get_cached_token(tenant_id: UUID, app_id: str) -> TokenResponse:
    """Get cached token for external app (used by S3)"""
    token_validator = TokenValidator()
    return await token_validator.get_valid_token(tenant_id, app_id)

@router.post("/tokens/revoke")
async def revoke_token(revoke_request: TokenRevokeRequest) -> RevocationResponse:
    """Revoke specific token by JTI"""
    token_validator = TokenValidator()
    await token_validator.revoke_token(revoke_request.jti, revoke_request.reason)
    return RevocationResponse(success=True)

@router.post("/tokens/global-logout")
async def global_logout(logout_request: GlobalLogoutRequest) -> LogoutResponse:
    """Global logout - revoke all tokens for user"""
    token_validator = TokenValidator()
    await token_validator.global_logout(logout_request.keycloak_user_id)
    return LogoutResponse(success=True)

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: UUID) -> UserResponse:
    """Get user information from Symphony (not Keycloak)"""
    user_repo = UserRepository()
    return await user_repo.get_by_id(user_id)

@router.post("/users", response_model=UserResponse)
async def create_user(user_create: UserCreate) -> UserResponse:
    """Create user in both Keycloak and Symphony"""
    user_repo = UserRepository()
    return await user_repo.create(user_create)