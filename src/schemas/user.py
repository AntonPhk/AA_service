import datetime
from typing import Annotated, Optional

from annotated_types import MaxLen, MinLen
from pydantic import EmailStr, HttpUrl, field_validator, BaseModel
from src.schemas.roles_and_permissions import RoleWithPermissionsSchema, RoleBaseSchema


class UserBaseSchema(BaseModel):
    name: Annotated[str, MinLen(3), MaxLen(15)]
    surname: Annotated[str, MinLen(3), MaxLen(15)]
    username: Annotated[str, MinLen(3), MaxLen(15)]
    email: Annotated[str, EmailStr]

    class Config:
        from_attributes = True


class PasswordSchema(BaseModel):
    password: str

    @field_validator("password")
    def validate_and_hash(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(char.isdigit() for char in value):
            raise ValueError("Password must contain at least one digit")
        if not any(char.isalpha() for char in value):
            raise ValueError("Password must contain at least one letter")
        return value


class UserRegistrationSchema(UserBaseSchema, PasswordSchema): ...


class UserPhotoSchema(BaseModel):
    image_url: HttpUrl


class UserUpdateSchema(BaseModel):
    name: Optional[Annotated[str, MinLen(3), MaxLen(15)]] = None
    surname: Optional[Annotated[str, MinLen(3), MaxLen(15)]] = None
    username: Optional[Annotated[str, MinLen(3), MaxLen(15)]] = None
    email: Optional[EmailStr] = None
    image_url: Optional[HttpUrl] = None


class UserUpdateByAdminSchema(UserUpdateSchema):
    password: Optional[PasswordSchema] = None
    role_id: Optional[int] = None


class UserResponseSchema(UserUpdateSchema):
    role: RoleBaseSchema


class UserResponseByAdminSchema(UserResponseSchema):
    role: RoleWithPermissionsSchema
    created_at: datetime.datetime
    updated_at: datetime.datetime
