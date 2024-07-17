from uuid import UUID

from starlette import status
from typing import Annotated, Optional, Any

from sqlalchemy.ext.asyncio import AsyncSession

from src.services.token_service import TokenService
from src.schemas.user import (
    UserRegistrationSchema,
    PasswordSchema,
    UserUpdateSchema,
    UserUpdateByAdminSchema,
)
from src.repositories.user_repository import UserRepository
from src.repositories.core import get_async_session
from sqlalchemy.exc import IntegrityError
from fastapi import Depends, HTTPException
from src.services.utils import (
    get_password_hash,
    verify_password,
    get_tokens,
)
from src.services.exceptions import (
    ExternalErrorException,
    IncorrectPasswordException,
    UserNotFoundException,
    DuplicateCredentialsException,
)


class UserService:
    def __init__(
        self,
        session: Annotated[AsyncSession, Depends(get_async_session)],
        token_service: TokenService,
    ) -> None:
        self.session = session
        self.repo = UserRepository(self.session)
        self.token_service = token_service

    async def signup(self, user: UserRegistrationSchema):
        try:
            user.password = get_password_hash(user.password)
            return await self.repo.create(user)
        except IntegrityError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=e.args[0][e.args[0].index("Key") :],
            )

    async def login(self, login: str, password: str):
        user = await self.repo.get(login)
        if not user:
            raise UserNotFoundException
        if verify_password(password, user.password):
            try:
                tokens = get_tokens(
                    data={
                        "user_id": str(user.id),
                        "user_role": str(user.role.name),
                    }
                )
                return tokens
            except Exception:
                raise ExternalErrorException
        else:
            raise IncorrectPasswordException

    async def change_password(self, token: str, password: PasswordSchema):
        payload = self.token_service.get_payload(token)
        password.password = get_password_hash(password=password.password)
        user_id = payload["user_id"]
        await self.repo.update(user_id, password)
        return {"detail": "Password updated successfully."}

    async def get_user(self, token: str):
        payload = self.token_service.get_payload(token=token)
        user_id = payload["user_id"]
        return await self.repo.get_by_id(user_id)

    async def get_user_by_id(self, token: str, user_id: UUID):
        self.token_service.validate_role(token, "admin")
        user = await self.repo.get_by_id(user_id=user_id)
        if not user:
            raise UserNotFoundException
        return user

    async def get_all_users(
        self,
        token: str,
        page: int = 1,
        limit: int = 10,
        order_by: str = "asc",
        filter_by_role: Optional[str] = None,
        sort_by: Any = None,
    ):
        self.token_service.validate_role(token, "admin")
        return await self.repo.get_all(
            page=page,
            limit=limit,
            order_by=order_by,
            filter_by_role=filter_by_role,
            sort_by=sort_by,
        )

    async def update_user(self, token: str, user: UserUpdateSchema):
        payload = self.token_service.get_payload(token)
        user_id = payload["user_id"]
        try:
            return await self.repo.update(user_id, user)
        except IntegrityError:
            raise DuplicateCredentialsException

    async def update_user_by_id(
        self, token: str, user_id: UUID, user: UserUpdateByAdminSchema
    ):
        self.token_service.validate_role(token, "admin")
        try:
            return await self.repo.update(entity_id=user_id, data=user)
        except IntegrityError:
            raise DuplicateCredentialsException

    async def delete_user(self, token: str):
        payload = self.token_service.get_payload(token)
        user_id = payload["user_id"]
        await self.repo.delete(user_id)
        return {"message": "User deleted successfully."}

    async def delete_user_by_id(self, token: str, user_id: UUID):
        self.token_service.validate_role(token, "admin")
        await self.repo.delete(user_id)
        return {"message": "User deleted successfully."}
