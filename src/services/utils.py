import string
from datetime import datetime, timedelta, timezone

from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from passlib.pwd import genword
import jwt
from src.core.config import settings
from src.schemas.token import TokenSchema

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
pwd_context = CryptContext(schemes=["bcrypt"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def get_random_password() -> str:
    return genword(entropy=56, length=16, chars=string.ascii_letters + string.digits)


def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=10000)
    to_encode.update({"exp": expire, "refresh": True})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_tokens(data: dict):
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data=data, expires_delta=access_token_expires)
    refresh_token = create_refresh_token(data=data)
    token_type = "Bearer"
    return TokenSchema(
        access_token=access_token, refresh_token=refresh_token, token_type=token_type
    )


def get_payload(token: str) -> dict:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return payload


class PermissionsValidator:
    @staticmethod
    def validate(role: str, required_role: str) -> bool:
        role_hierarchy = {"admin": ["admin", "user"], "user": ["user"]}
        return required_role in role_hierarchy.get(role, [])
