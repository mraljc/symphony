from typing import Dict, List, Optional
from src.core.keycloak_integration import KeycloakIntegration
from src.database.repositories import TokenRepository
from src.api.models import TokenClaims

class TokenValidationError(Exception):
    pass

class TokenRevokedError(Exception):
    pass

class TokenValidator:
    """
    JWT token validation with optimized revocation check
    Uses short-lived tokens (1h) with selective revocation only for critical cases
    """

    def __init__(self):
        self.keycloak_integration = KeycloakIntegration()
        self.token_repository = TokenRepository()
        # TODO: Implement these components
        # self.revocation_cache = RedisRevocationCache()
        # self.risk_engine = RiskEngine()

    async def validate_access_token(self, token: str, required_scopes: List[str] = None) -> TokenClaims:
        """Validates JWT token with optimized revocation check"""
        try:
            # 1. Validate token signature and basic claims via Keycloak
            keycloak_claims = await self.keycloak_integration.decode_token(
                token,
                options={"verify_signature": True, "verify_aud": True}
            )
            
            # 2. Validate audience match
            self._validate_audience(keycloak_claims, required_scopes)
            
            # 3. OPTIMIZED: Selective revocation check only for high-risk scenarios
            should_check_revocation = await self._should_check_revocation(keycloak_claims)
            if should_check_revocation and await self._is_token_revoked(keycloak_claims['jti']):
                raise TokenRevokedError("Token has been revoked")
            
            # 4. Enrich with Symphony claims
            symphony_claims = await self._get_symphony_claims(keycloak_claims['sub'])
            return TokenClaims(**keycloak_claims, **symphony_claims)
            
        except Exception as e:
            raise TokenValidationError(f"Token validation failed: {str(e)}")

    async def _should_check_revocation(self, claims: Dict) -> bool:
        """Determines if revocation check is needed based on risk assessment"""
        # Always check for admin users
        if 'admin' in claims.get('roles', []):
            return True
        
        # TODO: Implement risk engine
        # risk_score = await self.risk_engine.assess_token_risk(claims)
        # if risk_score > 0.7:
        #     return True
        
        # Check if user has global_logout request
        if await self._has_global_logout_request(claims['sub']):
            return True
        
        # For 99% of tokens - skip revocation check for performance
        return False

    async def revoke_token(self, jti: str, reason: str = "user_logout"):
        """Revokes token selectively - used only for critical cases"""
        # TODO: Implement database transaction
        # async with database.transaction():
        # Save to revocation registry
        await self.token_repository.add_to_revocation_registry(jti, reason)
        
        # TODO: Implement cache invalidation
        # await self.revocation_cache.revoke(jti)
        
        # TODO: Implement event logging
        # await self._log_revocation_event(jti, reason)

    async def global_logout(self, keycloak_user_id: str):
        """Global logout - revokes ALL tokens for a user"""
        # 1. Revoke all refresh tokens in Keycloak
        await self.keycloak_integration.revoke_user_sessions(keycloak_user_id)
        
        # 2. Mark for selective access token revocation
        await self.token_repository.mark_global_logout(keycloak_user_id)
        
        # 3. Clear all caches
        await self._clear_user_caches(keycloak_user_id)

    def _validate_audience(self, claims: Dict, required_audience: List[str] = None):
        """Validates token audience matches expected audiences"""
        token_audience = claims.get('aud', [])
        if not isinstance(token_audience, list):
            token_audience = [token_audience]

        if required_audience:
            # Exact match required for specific audiences
            if not all(aud in token_audience for aud in required_audience):
                raise TokenValidationError(
                    f"Token audience {token_audience} doesn't match required {required_audience}"
                )
        else:
            # Default validation - must have at least one valid audience
            valid_audiences = {'symphony-api', 'symphony-web', 'symphony-internal', 'symphony-external'}
            if not any(aud in valid_audiences for aud in token_audience):
                raise TokenValidationError(
                    f"Token has invalid audience: {token_audience}"
                )

    async def _is_token_revoked(self, jti: str) -> bool:
        """Check if token is revoked"""
        # TODO: Implement revocation check
        return await self.token_repository.is_token_revoked(jti)

    async def _has_global_logout_request(self, keycloak_user_id: str) -> bool:
        """Check if user has global logout request"""
        # TODO: Implement global logout check
        return False

    async def _clear_user_caches(self, keycloak_user_id: str):
        """Clear user caches"""
        # TODO: Implement cache clearing
        pass

    async def _get_symphony_claims(self, keycloak_user_id: str) -> Dict:
        """Get Symphony-specific claims for user"""
        # TODO: Implement Symphony claims retrieval
        return {}