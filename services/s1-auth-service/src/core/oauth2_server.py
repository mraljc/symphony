from typing import Dict, List, Optional
from uuid import UUID
from src.core.keycloak_integration import KeycloakIntegration
from src.database.repositories import UserRepository
from src.api.models import GrantRequest, TokenResponse

class UnsupportedGrantTypeError(Exception):
    pass

class OAuth2Error(Exception):
    pass

class OAuth2AuthorizationServer:
    """OAuth 2.0 Authorization Server - Thin facade in front of Keycloak"""
    
    SUPPORTED_GRANT_TYPES = {
        "authorization_code",  # With PKCE - PRIMARY for user authentication
        "refresh_token",       # For token refresh  
        "client_credentials"   # For service-to-service authentication
    }

    def __init__(self):
        self.keycloak_integration = KeycloakIntegration()
        self.user_repository = UserRepository()
        # TODO: Implement RateLimiter
        # self.rate_limiter = RateLimiter()

    async def issue_access_token(self, grant_request: GrantRequest) -> TokenResponse:
        """OAuth 2.0 token endpoint - delegates to Keycloak"""
        # 1. Validate grant type
        if grant_request.grant_type not in self.SUPPORTED_GRANT_TYPES:
            raise UnsupportedGrantTypeError(
                f"Unsupported grant type: {grant_request.grant_type}. " +
                "Supported: authorization_code, refresh_token, client_credentials"
            )
        
        # 2. Rate limiting (TODO: Implement)
        # await self.rate_limiter.check_limit(
        #     scope="token_issuance",
        #     identifier=grant_request.client_id
        # )
        
        # 3. Delegate to Keycloak
        try:
            if grant_request.grant_type == "authorization_code":
                keycloak_response = await self.keycloak_integration.token(
                    grant_type='authorization_code',
                    code=grant_request.code,
                    redirect_uri=grant_request.redirect_uri,
                    code_verifier=grant_request.code_verifier  # PKCE
                )
            elif grant_request.grant_type == "refresh_token":
                keycloak_response = await self.keycloak_integration.refresh_token(
                    grant_request.refresh_token
                )
            elif grant_request.grant_type == "client_credentials":
                keycloak_response = await self.keycloak_integration.client_credentials()
            
            # 4. Enrich response with Symphony-specific data
            return await self._enrich_token_response(keycloak_response)
            
        except Exception as e:  # TODO: Use specific KeycloakError
            raise OAuth2Error(f"Keycloak authentication failed: {str(e)}")

    async def _enrich_token_response(self, keycloak_response: Dict) -> TokenResponse:
        """Adds Symphony-specific claims to token response"""
        # Extract basic token data
        access_token = keycloak_response['access_token']
        refresh_token = keycloak_response.get('refresh_token')

        # Decode token to extract claims
        claims = await self.keycloak_integration.decode_token(access_token)

        # Get Symphony-specific user data
        symphony_user = await self.user_repository.get_by_keycloak_id(claims['sub'])

        # Create enriched token response
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="Bearer",
            expires_in=keycloak_response['expires_in'],
            scope=keycloak_response['scope'],
            symphony_context={
                "tenant_id": str(symphony_user.tenant_id),
                "user_preferences": symphony_user.symphony_user_preferences,
                "external_apps": symphony_user.external_app_authorizations
            }
        )
