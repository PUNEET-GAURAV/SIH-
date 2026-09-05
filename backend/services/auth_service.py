"""Auth service — user registration, login, token management."""

from typing import Optional

from sqlalchemy.orm import Session

from backend.models.user import User, UserRole
from backend.utils.security import hash_password, verify_password, create_access_token


class AuthService:
    """Business logic for authentication."""

    def __init__(self, db: Session):
        self.db = db

    def register_user(
        self,
        username: str,
        email: str,
        password: str,
        full_name: str = "",
        role: str = "officer",
    ) -> User:
        """Register a new user."""
        # Check for existing user
        existing = self.db.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()
        if existing:
            raise ValueError("Username or email already registered")

        user = User(
            username=username,
            email=email,
            password_hash=hash_password(password),
            full_name=full_name,
            role=UserRole(role),
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def authenticate(self, username: str, password: str) -> Optional[tuple[User, str]]:
        """Authenticate a user and return (user, token) or None."""
        user = self.db.query(User).filter(User.username == username).first()
        if not user or not verify_password(password, user.password_hash):
            return None
        if user.is_active != "true":
            return None

        token = create_access_token({"sub": user.id, "role": user.role.value})
        return user, token

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()
