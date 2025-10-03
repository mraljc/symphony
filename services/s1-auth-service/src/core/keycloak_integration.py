# TODO: Install required package: pip install python-keycloak

from keycloak import KeycloakAdmin, KeycloakOpenID
from typing import Dict, Optional
from src.config.settings import settings

class KeycloakError(Exception):
    pass

class KeycloakIntegration:
    """
    Keycloak integration for S1 Auth Service
    S1 functions as thin facade in front of Keycloak
    Keycloak handles: Users, Sessions, MFA, Password Policies, OIDC/OAuth 2.0 flows
    S1 handles: Business logic, External app tokens, Token cache, Symphony integration
    """

    def __init__(self):
        self.keycloak_admin = KeycloakAdmin(
            server_url=settings.keycloak_server_url,
            username=settings.keycloak_admin_user,
            password=settings.keycloak_admin_password,
            realm_name=settings.keycloak_realm
        )
        self.keycloak_openid = KeycloakOpenID(
            server_url=settings.keycloak_server_url,
            client_id=settings.keycloak_client_id,
            realm_name=settings.keycloak_realm,
            client_secret_key=settings.keycloak_client_secret
        )

    async def authenticate_user(self, username: str, password: str) -> Dict:
        """Delegates authentication to Keycloak"""
        try:
            return await self.keycloak_openid.token(username, password)
        except Exception as e:
            raise KeycloakError(f"Authentication failed: {str(e)}")

    async def create_user(self, user_data: Dict) -> str:
        """Creates user in Keycloak and syncs to Symphony"""
        try:
            # 1. Create user in Keycloak
            keycloak_user_id = self.keycloak_admin.create_user({
                'username': user_data['username'],
                'email': user_data['email'],
                'enabled': True,
                'credentials': [{
                    'type': 'password',
                    'value': user_data['password'],
                    'temporary': False
                }]
            })
            return keycloak_user_id
        except Exception as e:
            raise KeycloakError(f"User creation failed: {str(e)}")

    async def refresh_token(self, refresh_token: str) -> Dict:
        """Refreshes token using Keycloak"""
        try:
            return self.keycloak_openid.refresh_token(refresh_token)
        except Exception as e:
            raise KeycloakError(f"Token refresh failed: {str(e)}")

    async def client_credentials(self) -> Dict:
        """Gets Client credentials token"""
        try:
            return self.keycloak_openid.client_credentials()
        except Exception as e:
            raise KeycloakError(f"Client credentials failed: {str(e)}")

    async def decode_token(self, token: str, options: Dict = None) -> Dict:
        """Decodes and validates JWT token"""
        try:
            return self.keycloak_openid.decode_token(token, options=options)
        except Exception as e:
            raise KeycloakError(f"Token decoding failed: {str(e)}")

    async def revoke_user_sessions(self, user_id: str):
        """Revokes all sessions for user"""
        try:
            self.keycloak_admin.revoke_user_sessions(user_id)
        except Exception as e:
            raise KeycloakError(f"Session revocation failed: {str(e)}")

    async def token(self, grant_type: str, code: str = None, redirect_uri: str = None, code_verifier: str = None) -> Dict:
        """Generic token endpoint for various grant types"""
        try:
            return self.keycloak_openid.token(
                grant_type=grant_type,
                code=code,
                redirect_uri=redirect_uri,
                code_verifier=code_verifier
            )
        except Exception as e:
            raise KeycloakError(f"Token endpoint failed: {str(e)}")