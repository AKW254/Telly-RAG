from datetime import datetime, timedelta
from typing import Optional

from fastapi import status, HTTPException
from sqlalchemy.orm import Session

from app.models.users import User
from app.schemas.users_schema import UserCreate, UserLogin, UserUpdate, UserResponse, AuthResponse
from app.utils.auth import hash_password, verify_password, create_access_token
from app.tasks.mailer_tasks import onboarding_email_task
from app.config.settings import settings

class UserService:
    def __init__(self, db: Session):
        self.db = db

    def _user_query(self):
        return self.db.query(User)

    def _get_user_by_email(self, email: str) -> Optional[User]:
        return self._user_query().filter(User.email == email).first()

    def create_user(self, user_in: UserCreate) -> User:
        existing_user = self._get_user_by_email(user_in.email)
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

        hashed_password = hash_password(user_in.password)
        new_user = User(name=user_in.name, email=user_in.email, password=hashed_password)
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)

        onboarding_email_task.delay(new_user.email, new_user.name)
        return new_user

    def authenticate_user(self, user_in: UserLogin) -> AuthResponse:
        user = self._get_user_by_email(user_in.email)
        if not user or not verify_password(user_in.password, user.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
        return AuthResponse(access_token=access_token, token_type="bearer", user=UserResponse.model_validate(user))

    def update_user(self, user_id: int, user_in: UserUpdate) -> User:
        user = self._user_query().filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        if user_in.name:
            user.name = user_in.name
        if user_in.email:
            user.email = user_in.email
        if user_in.password:
            user.password = hash_password(user_in.password)

        self.db.commit()
        self.db.refresh(user)
        return user
