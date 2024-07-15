from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from src.schemas.user import UserBaseSchema, UserRegistrationSchema, PasswordSchema
from src.schemas.token import TokenSchema

from src.services.user_service import UserService
from src.api.dependencies import get_user_service
from src.services.utils import oauth2_scheme

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=UserBaseSchema)
async def signup(
    user: UserRegistrationSchema,
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.signup(user)


@router.post("/login", response_model=TokenSchema)
async def login_user(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.login(form_data.username, form_data.password)


@router.post("/change_password")
async def change_password(
    password: PasswordSchema,
    token: Annotated[str, Depends(oauth2_scheme)],
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.change_password(token=token, password=password)
