import jwt
from src.services.utils import get_payload, PermissionsValidator

from src.services.exceptions import (
    ExpiredTokenException,
    PermissionErrorException,
    InvalidTokenException,
)


class TokenService:
    def get_payload(self, token: str):
        try:
            return get_payload(token)
        except jwt.ExpiredSignatureError:
            raise ExpiredTokenException
        except jwt.InvalidTokenError:
            raise InvalidTokenException

    def validate_role(self, token: str, required_role: str):
        payload = self.get_payload(token)
        user_role = payload["user_role"]
        if not PermissionsValidator.validate(
            role=user_role, required_role=required_role
        ):
            raise PermissionErrorException
        return payload
