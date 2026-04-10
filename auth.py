from datetime import UTC, datetime, timedelta
import hashlib
import secrets
from typing import Annotated


from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import User
from config import settings
from database import get_db


PASWORD_HASHER = PasswordHash.recommended()

OAUTH2_SCHEME = OAuth2PasswordBearer(tokenUrl="api/users/token")


def hash_password(password: str) -> str:
    return PASWORD_HASHER.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return PASWORD_HASHER.verify(plain_password, hashed_password)

def generate_reset_token() -> str:
    return secrets.token_urlsafe(32)

def hash_reset_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta is not None:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY.get_secret_value(), 
        settings.ALGORITHM
    )
    return encoded_jwt

def verify_access_token(token: str) -> str | None:
    """Verify a JWT access token and return the subject (user ID) if valid."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY.get_secret_value(),
            settings.ALGORITHM,
            options={"require": ["exp", "sub"]},
        )
    except (jwt.InvalidTokenError, jwt.ExpiredSignatureError):
        return None
    else:
        return payload.get("sub")


async def get_current_user(
    token: Annotated[str, Depends(OAUTH2_SCHEME)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    user_id = verify_access_token(token)
    if user_id is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED,
                            "Invalid or expired token",
                            headers={"WWW-Authenticate": "Bearer"})
    try:
        user_id_int = int(user_id)
    except (TypeError, ValueError):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED,
                            "Invalid or expired token",
                            headers={"WWW-Authenticate": "Bearer"})
    result = await db.execute(
        select(User)
        .where(User.id == user_id_int),
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED,
                            "User not found",
                            headers={"WWW-Authenticate": "Bearer"})
    return user

CurrentUser = Annotated[User, Depends(get_current_user)]
