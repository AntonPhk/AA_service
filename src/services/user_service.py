from uuid import UUID

import jwt
from starlette import status
from typing import Annotated, Optional, Any

from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.user import UserRegistrationSchema, PasswordSchema, UserUpdateSchema
from src.services.utils import PermissionsValidator
from src.repositories.user_repository import UserRepository
from src.repositories.core import get_async_session
from sqlalchemy.exc import IntegrityError
from fastapi import Depends, HTTPException
from src.services.utils import (
    get_password_hash,
    verify_password,
    get_tokens,
    get_payload,
)
from src.services.exceptions import (
    ExternalErrorException,
    CredentialsException,
    InvalidPasswordException,
    IncorrectPasswordException,
    UserNotFoundException,
    ExpiredTokenException,
)


class UserService:
    def __init__(
        self, session: Annotated[AsyncSession, Depends(get_async_session)]
    ) -> None:
        self.session = session
        self.db = UserRepository(self.session)

    async def signup(self, user: UserRegistrationSchema):
        try:
            user.password = get_password_hash(user.password)
            result = await self.db.create(user)
            return result
        except IntegrityError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=e.args[0][e.args[0].index("Key") :],
            )

    async def login(self, login: str, password: str):
        user = await self.db.get(login)
        if not user:
            raise UserNotFoundException
        if verify_password(password, user.password):
            try:
                user_id = str(user.id)
                user_role = str(user.role.name)
                print(user_id, user_role)
                tokens = get_tokens(
                    data={
                        "user_id": user_id,
                        "user_role": user_role,
                    }
                )
                return tokens
            except Exception:
                raise ExternalErrorException
        else:
            raise IncorrectPasswordException

    async def change_password(self, token: str, password: PasswordSchema):
        try:
            payload = get_payload(token)
            password.password = get_password_hash(password=password.password)
            user_id = payload["user_id"]
            await self.db.update(user_id, password)
            return {"message": "Password updated successfully."}
        except jwt.ExpiredSignatureError:
            raise ExpiredTokenException
        except jwt.InvalidTokenError:
            raise CredentialsException

    async def get_user(self, token: str):
        try:
            payload = get_payload(token)
            user_id = payload["user_id"]

            return await self.db.get_by_id(user_id)
        except jwt.ExpiredSignatureError:
            raise ExpiredTokenException
        except jwt.InvalidTokenError:
            raise CredentialsException
        except ValueError:
            raise InvalidPasswordException
        except Exception:
            raise ExternalErrorException

    async def get_user_by_id(self, token: str, user_id: UUID):
        try:
            payload = get_payload(token)
            user_role = payload["user_role"]

        except jwt.ExpiredSignatureError:
            raise ExpiredTokenException
        except jwt.InvalidTokenError:
            raise CredentialsException
        if PermissionsValidator.validate(role=user_role):
            user = await self.db.get_by_id(user_id=user_id)
            if not user:
                raise UserNotFoundException
            else:
                return user
        else:
            raise CredentialsException

    async def get_all_users(
        self,
        token: str,
        page: int = 1,
        limit: int = 10,
        order_by: str = "asc",
        filter_by_role: Optional[str] = None,
        sort_by: Any = None,
    ):
        try:
            payload = get_payload(token)
            user_role = payload["user_role"]

        except jwt.ExpiredSignatureError:
            raise ExpiredTokenException
        except jwt.InvalidTokenError:
            raise CredentialsException
        if PermissionsValidator.validate(role=user_role):
            user = await self.db.get_all(
                page=page,
                limit=limit,
                order_by=order_by,
                filter_by_role=filter_by_role,
                sort_by=sort_by,
            )
            return user
        else:
            raise CredentialsException

    async def update_user(self, token: str, user: UserUpdateSchema):
        try:
            payload = get_payload(token)
            user_id = payload["user_id"]

            return await self.db.update(user_id, user)
        except jwt.ExpiredSignatureError:
            raise ExpiredTokenException
        except jwt.InvalidTokenError:
            raise CredentialsException

    async def update_user_by_id(
        self, token: str, user_id: UUID, user: UserUpdateSchema
    ):
        try:
            payload = get_payload(token)
            user_role = payload["user_role"]
        except jwt.ExpiredSignatureError:
            raise ExpiredTokenException
        except jwt.InvalidTokenError:
            raise CredentialsException

        if PermissionsValidator.validate(role=user_role):
            return await self.db.update(user_id=user_id, data=user)
        else:
            raise CredentialsException

    async def delete_user(self, token: str):
        try:
            payload = get_payload(token)
            user_id = payload["user_id"]

            await self.db.delete(user_id)
            return {"message": "User deleted successfully."}
        except jwt.ExpiredSignatureError:
            raise ExpiredTokenException
        except jwt.InvalidTokenError:
            raise CredentialsException

    async def delete_user_by_id(self, token: str, user_id: UUID):
        try:
            payload = get_payload(token)
            user_role = payload["user_role"]
        except jwt.ExpiredSignatureError:
            raise ExpiredTokenException
        except jwt.InvalidTokenError:
            raise CredentialsException

        if user_role == "admin":
            await self.db.delete(user_id)
            return {"message": "User deleted successfully."}
        else:
            raise CredentialsException
