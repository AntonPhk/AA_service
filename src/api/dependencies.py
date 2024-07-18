from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession

from src.services.permission_service import PermissionService
from src.services.role_service import RoleService
from src.services.user_service import UserService
from src.repositories.core import get_async_session
from fastapi import Depends
from src.services.token_service import TokenService
from additional_services.mail_sender import EmailSender


def get_email_sender() -> EmailSender:
    return EmailSender()


def get_token_service() -> TokenService:
    return TokenService()


def get_user_service(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    mail_sender: Annotated[EmailSender, Depends(get_email_sender)],
    token_src: TokenService = Depends(get_token_service),
) -> UserService:
    return UserService(
        session=session, token_service=token_src, mail_sender=mail_sender
    )


def get_role_service(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    token_src: TokenService = Depends(get_token_service),
) -> RoleService:
    return RoleService(session=session, token_service=token_src)


def get_permission_service(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    token_src: TokenService = Depends(get_token_service),
) -> PermissionService:
    return PermissionService(session=session, token_service=token_src)
