from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from uuid import UUID
from datetime import datetime

class GrantRequest(BaseModel):
    grant_type: str = Field(..., description="authorization_code, refresh_token, or client_credentials")
    code: Optional[str] = None
    redirect_uri: Optional[str] = None
    code_verifier: Optional[str] = None
    refresh_token: Optional[str] = None
    client_id: str
    client_secret: Optional[str] = None
    scope: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "Bearer"
    expires_in: int
    scope: str
    symphony_context: Dict[str, Any] = Field(default_factory=dict)

class TokenRevokeRequest(BaseModel):
    jti: str = Field(..., description="JWT ID to revoke")
    reason: str = Field(..., description="user_logout, admin_revoke, security_incident")

class RevocationResponse(BaseModel):
    success: bool
    revoked_at: datetime = Field(default_factory=datetime.utcnow)

class GlobalLogoutRequest(BaseModel):
    keycloak_user_id: str = Field(..., description="Keycloak user ID")

class LogoutResponse(BaseModel):
    success: bool
    tokens_revoked: int
    revoked_at: datetime = Field(default_factory=datetime.utcnow)

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    password: str = Field(..., min_length=8)
    tenant_id: UUID
    symphony_user_preferences: Dict[str, Any] = Field(default_factory=dict)

class UserResponse(BaseModel):
    id: UUID
    keycloak_user_id: str
    tenant_id: UUID
    symphony_user_preferences: Dict[str, Any]
    external_app_authorizations: List[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

class TokenClaims(BaseModel):
    sub: str = Field(..., description="Subject (user ID)")
    exp: int = Field(..., description="Expiration time")
    iat: int = Field(..., description="Issued at")
    jti: str = Field(..., description="JWT ID")
    tenant_id: UUID
    roles: List[str] = Field(default_factory=list)
    symphony_context: Dict[str, Any] = Field(default_factory=dict)