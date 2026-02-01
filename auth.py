from datetime import datetime, timedelta, UTC

import jwt
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash

from config import settings


PASWORD_HASHER = PasswordHash.recommended()

OAUTH2_SCHEME = OAuth2PasswordBearer(tokenUrl="api/users/token")


def hash_password(password: str) -> str:
    return PASWORD_HASHER.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return PASWORD_HASHER.verify(plain_password, hashed_password)

def create_access_token(
    data: dict, expires_delta: timedelta | None = None
) -> str:
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
            algorithms=[settings.ALGORITHM],
            options={"require": ["exp", "sub"]}
        )
    except (jwt.InvalidTokenError, jwt.ExpiredSignatureError):
        return None
    else:
        return payload.get("sub")