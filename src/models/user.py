from typing import List
from uuid import UUID, uuid4

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.core import BaseModel, Base


class RolesAndPermissions(Base):
    __tablename__ = "roles_permissions_association"

    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), primary_key=True)
    permission_id: Mapped[int] = mapped_column(
        ForeignKey("permissions.id"), primary_key=True
    )


class Roles(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    users: Mapped[List["Users"]] = relationship(back_populates="role")
    permissions: Mapped[List["Permissions"]] = relationship(
        secondary="roles_permissions_association",
        back_populates="roles",
    )


class Permissions(Base):
    __tablename__ = "permissions"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    roles: Mapped[List["Roles"]] = relationship(
        secondary="roles_permissions_association",
        back_populates="permissions",
    )


class Users(BaseModel):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str]
    surname: Mapped[str]
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str] = mapped_column(String(80))
    email: Mapped[str] = mapped_column(unique=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), default=1)
    role: Mapped["Roles"] = relationship(back_populates="users")
    image_url: Mapped[str] = mapped_column(String(128), nullable=True)
