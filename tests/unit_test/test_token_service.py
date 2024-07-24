from src.services.exceptions import (
    PermissionErrorException,
    ExpiredTokenException,
    InvalidTokenException,
)
from src.services.token_service import TokenService
import pytest


@pytest.mark.asyncio
class TestTokenService:
    token_service = TokenService()

    @pytest.mark.parametrize("add_user", ["base"], indirect=True)
    async def test_get_payload(self, get_access_token):
        payload = self.token_service.get_payload(get_access_token)
        assert payload != ""

    async def test_get_payload_with_expired_token(self, get_expired_token):
        with pytest.raises(ExpiredTokenException):
            self.token_service.get_payload(get_expired_token)

    async def test_get_payload_with_invalid_token(self, get_invalid_token):
        with pytest.raises(InvalidTokenException):
            self.token_service.get_payload(get_invalid_token)

    @pytest.mark.parametrize(
        "add_user, user_role",
        [("base", "user"), ("base", "admin")],
        indirect=["add_user"],
    )
    async def test_validate_role(self, get_access_token, user_role: str):
        if user_role == 1:
            result = self.token_service.validate_role(get_access_token, user_role)
            assert result

        elif user_role == 2:
            with pytest.raises(PermissionErrorException):
                self.token_service.validate_role(get_access_token, user_role)
