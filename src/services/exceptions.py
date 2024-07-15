from fastapi import HTTPException
from starlette import status


class ExternalErrorException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Something went wrong. Try again later",
        )


class CredentialsException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )


class IncorrectPasswordException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password"
        )


class ExpiredTokenException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail="Token expired")


class InvalidUUIDException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid UUID.")


class PermissionErrorException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You have no permission to perform this action",
        )


class UserNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


class BlacklistedTokenException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail="Unable to do this action",
        )


class InvalidPasswordException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Invalid password"
        )


class DuplicateCredentialsException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this username/phone number/email already exists.",
        )
