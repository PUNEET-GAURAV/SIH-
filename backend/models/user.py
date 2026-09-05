"""User model for authentication and RBAC."""

import enum

from sqlalchemy import Column, String, Enum
from backend.models.base import Base, TimestampMixin, generate_uuid


class UserRole(str, enum.Enum):
    OFFICER = "officer"
    SUPERVISOR = "supervisor"
    ADMIN = "admin"


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False, default="")
    role = Column(Enum(UserRole), nullable=False, default=UserRole.OFFICER)
    is_active = Column(String(5), nullable=False, default="true")  # SQLite compatible bool
