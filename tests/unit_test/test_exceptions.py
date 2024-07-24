import pytest
from fastapi import status
from src.services.exceptions import (
    ExternalErrorException,
    NotVerifiedCredentialsException,
    IncorrectPasswordException,
    ExpiredTokenException,
    InvalidTokenException,
    PermissionErrorException,
    UserNotFoundException,
    RoleNotFoundException,
    PermissionNotFoundException,
    BlacklistedTokenException,
    DuplicateCredentialsException,
    DuplicateRoleException,
    DuplicatePermissionException,
)


@pytest.mark.asyncio
class TestHTTPExceptions:
    async def test_external_error_exception(self):
        with pytest.raises(ExternalErrorException) as exc_info:
            raise ExternalErrorException()
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert exc_info.value.detail == "Something went wrong. Try again later"

    async def test_not_verified_credentials_exception(self):
        with pytest.raises(NotVerifiedCredentialsException) as exc_info:
            raise NotVerifiedCredentialsException()
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == "User haven't been verified, check your email."

    async def test_incorrect_password_exception(self):
        with pytest.raises(IncorrectPasswordException) as exc_info:
            raise IncorrectPasswordException()
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == "Incorrect password"

    async def test_expired_token_exception(self):
        with pytest.raises(ExpiredTokenException) as exc_info:
            raise ExpiredTokenException()
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert exc_info.value.detail == "Token expired"

    async def test_invalid_token_exception(self):
        with pytest.raises(InvalidTokenException) as exc_info:
            raise InvalidTokenException()
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert exc_info.value.detail == "Invalid token"

    async def test_permission_error_exception(self):
        with pytest.raises(PermissionErrorException) as exc_info:
            raise PermissionErrorException()
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert exc_info.value.detail == "You have no permission to perform this action"

    async def test_user_not_found_exception(self):
        with pytest.raises(UserNotFoundException) as exc_info:
            raise UserNotFoundException()
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert exc_info.value.detail == "User not found"

    async def test_role_not_found_exception(self):
        with pytest.raises(RoleNotFoundException) as exc_info:
            raise RoleNotFoundException()
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert exc_info.value.detail == "Role not found"

    async def test_permission_not_found_exception(self):
        with pytest.raises(PermissionNotFoundException) as exc_info:
            raise PermissionNotFoundException()
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert exc_info.value.detail == "Permission not found"

    async def test_blacklisted_token_exception(self):
        with pytest.raises(BlacklistedTokenException) as exc_info:
            raise BlacklistedTokenException()
        assert exc_info.value.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        assert exc_info.value.detail == "Unable to do this action"

    async def test_duplicate_credentials_exception(self):
        with pytest.raises(DuplicateCredentialsException) as exc_info:
            raise DuplicateCredentialsException()
        assert exc_info.value.status_code == status.HTTP_409_CONFLICT
        assert (
            exc_info.value.detail
            == "User with this username/phone number/email already exists."
        )

    async def test_duplicate_role_exception(self):
        with pytest.raises(DuplicateRoleException) as exc_info:
            raise DuplicateRoleException()
        assert exc_info.value.status_code == status.HTTP_409_CONFLICT
        assert exc_info.value.detail == "Role already exists."

    async def test_duplicate_permission_exception(self):
        with pytest.raises(DuplicatePermissionException) as exc_info:
            raise DuplicatePermissionException()
        assert exc_info.value.status_code == status.HTTP_409_CONFLICT
        assert exc_info.value.detail == "Permission already exists."
