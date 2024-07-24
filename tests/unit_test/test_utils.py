from src.services.utils import get_random_password, get_password_hash, verify_password
import pytest


@pytest.fixture(scope="class")
def random_password():
    return get_random_password()


@pytest.fixture(scope="class")
def password_hash(random_password):
    return get_password_hash(random_password)


@pytest.mark.asyncio
class TestUtils:
    async def test_get_random_password(self, random_password):
        assert random_password != ""
        assert len(random_password) >= 8

    @pytest.mark.parametrize("add_user", ["base"], indirect=True)
    async def test_create_access_token(self, get_access_token):
        assert get_access_token != ""

    async def test_create_refresh_token(self, get_refresh_token):
        assert get_refresh_token != ""

    async def test_get_tokens(self, create_tokens):
        assert create_tokens != ""

    async def test_get_password_hash(self, random_password, password_hash):
        assert password_hash != ""
        assert password_hash != random_password
        assert password_hash.startswith("$")

    async def test_verify_password(self, random_password, password_hash):
        assert verify_password(random_password, password_hash)

    async def test_verify_invalid_password(self, password_hash):
        invalid_password = get_random_password()
        assert verify_password(invalid_password, password_hash) is False
