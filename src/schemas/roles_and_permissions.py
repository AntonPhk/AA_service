from typing import List

from pydantic import BaseModel


class PermissionBaseSchema(BaseModel):
    name: str


class PermissionResponseSchema(PermissionBaseSchema):
    id: int


class RoleBaseSchema(BaseModel):
    name: str


class RoleResponseSchema(RoleBaseSchema):
    id: int


class RoleWithPermissionsSchema(RoleResponseSchema):
    permissions: List[PermissionResponseSchema]
