from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.users_schema import (
    UserCreate,
    UserLogin,
    UserUpdate,
    UserResponse,
    AuthResponse,
)
from app.models.users import User

from app.api.dependencies import get_current_user
from app.services.users_service import UserService


router = APIRouter()


# ==================================================
# Routes
# ==================================================

@router.post(
    "/register",
    response_model=UserResponse,
)
def register(
    user_in: UserCreate,
    db: Session = Depends(get_db),
) -> UserResponse:
    user_service = UserService(db)
    return user_service.create_user(user_in)


@router.post(
    "/login",
    response_model=AuthResponse,
)
def login(
    user_in: UserLogin,
    db: Session = Depends(get_db),
) -> AuthResponse:
    user_service = UserService(db)
    return user_service.authenticate_user(user_in)


@router.get(
    "/me",
    response_model=UserResponse,
)
def profile(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    return current_user


@router.put(
    "/me",
    response_model=UserResponse,
)
def update_profile(
    user_in: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserResponse:
    user_service = UserService(db)

    return user_service.update_user(
        current_user.id,
        user_in,
    )
