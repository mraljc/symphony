import pytest
from unittest.mock import Mock, patch
from src.core.oauth2_server import OAuth2AuthorizationServer, UnsupportedGrantTypeError
from src.api.models import GrantRequest

class TestOAuth2AuthorizationServer:
    @pytest.fixture
    def oauth_server(self):
        return OAuth2AuthorizationServer()

    @pytest.mark.asyncio
    async def test_issue_token_authorization_code(self, oauth_server):
        """Test authorization code grant flow"""
        grant_request = GrantRequest(
            grant_type="authorization_code",
            code="test_code",
            redirect_uri="https://app.example.com/callback",
            code_verifier="test_verifier",
            client_id="test_client"
        )
        with patch.object(oauth_server.keycloak_integration, 'token') as mock_keycloak:
            mock_keycloak.return_value = {
                'access_token': 'test_access_token',
                'refresh_token': 'test_refresh_token',
                'expires_in': 3600,
                'scope': 'openid profile'
            }
            result = await oauth_server.issue_access_token(grant_request)

            assert result.access_token == 'test_access_token'
            assert result.token_type == 'Bearer'
            mock_keycloak.assert_called_once_with(
                grant_type='authorization_code',
                code='test_code',
                redirect_uri="https://app.example.com/callback",
                code_verifier="test_verifier"
            )

    @pytest.mark.asyncio
    async def test_unsupported_grant_type(self, oauth_server):
        """Test rejection of unsupported grant types"""
        grant_request = GrantRequest(
            grant_type="password",  # Not supported
            client_id="test_client"
        )
        with pytest.raises(UnsupportedGrantTypeError):
            await oauth_server.issue_access_token(grant_request)