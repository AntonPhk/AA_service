from typing import List
from uuid import UUID, uuid4

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.core import BaseModel, Base


class RolesAndPermissions(Base):
    __tablename__ = "roles_permissions_association"

    role_id: Mapped[int] = mapped_column(ForeignKey("role.id"), primary_key=True)
    permission_id: Mapped[int] = mapped_column(
        ForeignKey("permission.id"), primary_key=True
    )


class Role(Base):
    __tablename__ = "role"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    users: Mapped[List["User"]] = relationship(back_populates="role")
    permissions: Mapped[List["Permission"]] = relationship(
        secondary="roles_permissions_association",
        back_populates="roles",
    )


class Permission(Base):
    __tablename__ = "permission"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    roles: Mapped[List["Role"]] = relationship(
        secondary="roles_permissions_association",
        back_populates="permissions",
    )


class User(BaseModel):
    __tablename__ = "user"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str]
    surname: Mapped[str]
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str] = mapped_column(String(80))
    email: Mapped[str] = mapped_column(unique=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("role.id"), default=1)
    role: Mapped["Role"] = relationship(back_populates="users")
    image_url: Mapped[str] = mapped_column(String(128), nullable=True)
