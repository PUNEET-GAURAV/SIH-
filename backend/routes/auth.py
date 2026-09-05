"""Auth routes — registration and login. Thin route layer, logic in service."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.schemas import APIResponse, UserCreate, UserLogin, UserResponse, TokenResponse
from backend.services.auth_service import AuthService
from backend.utils.security import get_current_user
from backend.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
def register(payload: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    service = AuthService(db)
    try:
        user = service.register_user(
            username=payload.username,
            email=payload.email,
            password=payload.password,
            full_name=payload.full_name,
            role=payload.role,
        )
        return APIResponse(
            data=UserResponse.model_validate(user).model_dump()
        ).model_dump()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login")
def login(payload: UserLogin, db: Session = Depends(get_db)):
    """Authenticate and get a JWT token."""
    service = AuthService(db)
    result = service.authenticate(payload.username, payload.password)
    if not result:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    user, token = result
    return APIResponse(
        data=TokenResponse(
            access_token=token,
            user=UserResponse.model_validate(user),
        ).model_dump()
    ).model_dump()


@router.get("/me")
def get_me(user: User = Depends(get_current_user)):
    """Get current user profile."""
    return APIResponse(
        data=UserResponse.model_validate(user).model_dump()
    ).model_dump()
