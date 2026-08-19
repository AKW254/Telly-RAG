
from typing import Optional
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.users import User
from app.utils.auth import decode_access_token


bearer_scheme = HTTPBearer(auto_error=False)


# -----------------------------
# Exceptions
# -----------------------------
def _unauthorized_exception(detail: str = "Authentication required") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


# -----------------------------
# Get user from JWT subject
# -----------------------------
def _get_user_from_subject(db: Session, subject: str) -> Optional[User]:
    """
    subject can be:
    - user id (integer serialized as string)
    - email (string)
    """

    if subject.isdigit():
        user = db.query(User).filter(User.id == int(subject)).first()
        if user:
            return user

    return db.query(User).filter(User.email == subject).first()


# -----------------------------
# Core resolver (token → user)
# -----------------------------
def _resolve_user_from_credentials(
    credentials: Optional[HTTPAuthorizationCredentials],
    db: Session,
    *,
    required: bool
) -> Optional[User]:

    if credentials is None:
        if required:
            raise _unauthorized_exception("Authentication required")
        return None

    token = credentials.credentials

    try:
        payload = decode_access_token(token)
    except jwt.ExpiredSignatureError:
        raise _unauthorized_exception("Token has expired")
    except jwt.InvalidTokenError:
        raise _unauthorized_exception("Invalid token")

    subject = payload.get("sub")

    if not subject:
        raise _unauthorized_exception("Invalid token payload")

    user = _get_user_from_subject(db, str(subject))

    if not user:
        raise _unauthorized_exception("User not found")

    return user


# -----------------------------
# Dependency: Get current user
# -----------------------------
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:

    return _resolve_user_from_credentials(
        credentials,
        db,
        required=True
    )