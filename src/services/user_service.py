from datetime import timedelta
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
    ConfirmationAcceptSchema,
)
from src.repositories.user_repository import UserRepository
from src.repositories.core import get_async_session
from sqlalchemy.exc import IntegrityError
from fastapi import Depends, HTTPException
from src.services.utils import (
    verify_password,
    get_tokens,
    create_access_token,
    get_random_password,
)
from src.services.exceptions import (
    ExternalErrorException,
    IncorrectPasswordException,
    UserNotFoundException,
    DuplicateCredentialsException,
    NotVerifiedCredentialsException,
)
from additional_services.mail_sender import EmailSender
from additional_services.token_warehouse import TokenWarehouse


class UserService:
    def __init__(
        self,
        session: Annotated[AsyncSession, Depends(get_async_session)],
        mail_sender: EmailSender,
        token_service: TokenService,
    ) -> None:
        self._session = session
        self._mail_sender = mail_sender
        self._repo = UserRepository(self._session)
        self._token_service = token_service
        self._token_warehouse = TokenWarehouse()

    async def signup(self, user: UserRegistrationSchema):
        try:
            new_user = await self._repo.create(user)
            unic_jwt = create_access_token(
                data={"user_id": str(new_user.id)}, expires_delta=timedelta(minutes=30)
            )
            if await self._mail_sender.send_accept_registration_email(
                new_user.email, unic_jwt
            ):
                return {"message": "To confirm registration, check your email."}
        except IntegrityError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=e.args[0][e.args[0].index("Key") :],
            )

    async def send_confirmation_again(self, email: str):
        user = await self._repo.get(email)
        if not user:
            raise UserNotFoundException
        if not user.is_verified:
            unic_jwt = create_access_token(
                data={"user_id": str(user.id)}, expires_delta=timedelta(minutes=30)
            )
            if await self._mail_sender.send_accept_registration_email(
                user.email, unic_jwt
            ):
                return {"message": "To confirm registration, check your email."}
        else:
            return {"message": "User has been verified"}

    async def confirm_registration(self, token: str):
        payload = self._token_service.get_payload(token)
        user_id = payload["user_id"]
        verified = ConfirmationAcceptSchema(is_verified=True)
        await self._repo.update(user_id, verified)
        return {"message": "Registration confirmed."}

    async def login(self, login: str, password: str):
        user = await self._repo.get(login)
        if not user:
            raise UserNotFoundException
        if not user.is_verified:
            raise NotVerifiedCredentialsException
        if verify_password(password, user.password):
            try:
                tokens = get_tokens(
                    data={"user_id": str(user.id), "user_role": str(user.role.name)}
                )
                await self._token_warehouse.add_token_to_redis(
                    user_id=user.id, token=tokens.refresh_token
                )
                return tokens
            except Exception:
                raise ExternalErrorException
        else:
            raise IncorrectPasswordException

    async def change_password(self, token: str, password: PasswordSchema):
        payload = self._token_service.get_payload(token)
        user_id = payload["user_id"]
        await self._repo.update(user_id, password)
        return {"detail": "Password updated successfully."}

    async def request_reset_password(self, email: str):
        user = await self._repo.get(email)
        if not user:
            raise UserNotFoundException
        unic_jwt = create_access_token(
            data={"user_id": str(user.id)}, expires_delta=timedelta(minutes=30)
        )
        if await self._mail_sender.send_reset_password_email(user.email, unic_jwt):
            return {"message": "To reset your password, check your email."}

    async def reset_password(self, token: str):
        payload = self._token_service.get_payload(token)
        user_id = payload["user_id"]
        new_password = get_random_password()
        new_password_schema = PasswordSchema(password=new_password)
        await self._repo.update(user_id, new_password_schema)
        return {
            "message": f"Password has been reset successfully. New password is {new_password}"
        }

    async def get_new_tokens(self, token: str):
        payload = self._token_service.get_payload(token)
        user_id = payload["user_id"]
        if await self._token_warehouse.is_token_exist(user_id):
            user = await self._repo.get_by_id(user_id)
            new_tokens = get_tokens(
                data={"user_id": str(user.id), "user_role": str(user.role.name)}
            )
            await self._token_warehouse.add_token_to_redis(
                user_id=user.id, token=new_tokens.refresh_token
            )
            return new_tokens

    async def get_user(self, token: str):
        payload = self._token_service.get_payload(token=token)
        user_id = payload["user_id"]
        return await self._repo.get_by_id(user_id)

    async def get_user_by_id(self, token: str, user_id: UUID):
        self._token_service.validate_role(token, "admin")
        user = await self._repo.get_by_id(user_id=user_id)
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
        self._token_service.validate_role(token, "admin")
        return await self._repo.get_all(
            page=page,
            limit=limit,
            order_by=order_by,
            filter_by_role=filter_by_role,
            sort_by=sort_by,
        )

    async def update_user(self, token: str, user: UserUpdateSchema):
        payload = self._token_service.get_payload(token)
        user_id = payload["user_id"]
        try:
            return await self._repo.update(user_id, user)
        except IntegrityError:
            raise DuplicateCredentialsException

    async def update_user_by_id(
        self, token: str, user_id: UUID, user: UserUpdateByAdminSchema
    ):
        self._token_service.validate_role(token, "admin")
        try:
            return await self._repo.update(entity_id=user_id, data=user)
        except IntegrityError:
            raise DuplicateCredentialsException

    async def delete_user(self, token: str):
        payload = self._token_service.get_payload(token)
        user_id = payload["user_id"]
        await self._repo.delete(user_id)
        return {"message": "User deleted successfully."}

    async def delete_user_by_id(self, token: str, user_id: UUID):
        self._token_service.validate_role(token, "admin")
        await self._repo.delete(user_id)
        return {"message": "User deleted successfully."}
