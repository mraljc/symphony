import pytest
from unittest.mock import Mock, patch
from src.core.token_validator import TokenValidator, TokenValidationError, TokenRevokedError

class TestTokenValidator:
    @pytest.fixture
    def token_validator(self):
        return TokenValidator()

    @pytest.mark.asyncio
    async def test_validate_token_success(self, token_validator):
        """Test successful token validation"""
        test_token = "valid.jwt.token"

        with patch.object(token_validator.keycloak_integration, 'decode_token') as mock_decode:
            mock_decode.return_value = {
                'sub': 'user123',
                'exp': 1234567890,
                'iat': 1234567890,
                'jti': 'token123',
                'aud': ['symphony-api']
            }
            with patch.object(token_validator, '_should_check_revocation') as mock_revocation:
                mock_revocation.return_value = False

                result = await token_validator.validate_access_token(test_token)

                assert result.sub == 'user123'
                mock_decode.assert_called_once_with(test_token, {
                    'verify_signature': True,
                    'verify_aud': True
                })

    @pytest.mark.asyncio
    async def test_validate_token_revoked(self, token_validator):
        """Test validation of revoked token"""
        test_token = "revoked.jwt.token"

        with patch.object(token_validator.keycloak_integration, 'decode_token') as mock_decode:
            mock_decode.return_value = {
                'sub': 'user123',
                'exp': 1234567890,
                'iat': 1234567890,
                'jti': 'revoked_token',
                'aud': ['symphony-api']
            }

            with patch.object(token_validator, '_should_check_revocation') as mock_revocation:
                mock_revocation.return_value = True

                with patch.object(token_validator, '_is_token_revoked') as mock_revoked:
                    mock_revoked.return_value = True

                    with pytest.raises(TokenRevokedError):
                        await token_validator.validate_access_token(test_token)