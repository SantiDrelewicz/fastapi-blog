from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from auth import (
    OAUTH2_SCHEME,
    create_access_token, 
    hash_password, 
    verify_access_token, 
    verify_password
)
from config import settings
from database import get_db
from models import Post, User
from schemas import (
    PostResponse, Token, UserCreate, UserPrivate, UserPublic, UserUpdate
)


router = APIRouter()



@router.post(
    "",
    response_model=UserPrivate,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(user: UserCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    existing_username = await db.execute(
        select(User)
        .where(func.lower(User.username) == user.username.lower())
    )
    if existing_username.scalar():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )

    existing_email = await db.execute(
        select(User)
        .where(func.lower(User.email) == user.email.lower()),
    )
    if existing_email.scalar():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    new_user = User(
        username=user.username,
        email=user.email.lower(),
        password_hash=hash_password(user.password),
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return new_user


@router.post("/token", response_model=Token)
async def login_for_access_token( 
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    # Look up user by email (case-insensitive)
    # Note: OAuth2PasswordBearer uses 'username' field, but we treat it as email.
    user = await db.scalar(
        select(User)
        .where(func.lower(User.email) == form_data.username.lower()),
    )
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, "Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Create access token with user id as subject
    access_token = create_access_token(
        {"sub": str(user.id)}, 
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserPrivate)
async def get_current_user(
    token: Annotated[str, Depends(OAUTH2_SCHEME)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get the currently authenticated user."""
    user_id = verify_access_token(token)
    if user_id is None:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, "Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Validate user_id is a valid integer (defense against malformded JWT)
    try:
        user_id_int = int(user_id)
    except (TypeError, ValueError):
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, "Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = await db.scalar(
        select(User)
        .where(User.id == user_id_int)
    )
    if user is None:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, "User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


@router.get("/{user_id}", response_model=UserPublic)
async def get_user(user_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    user = await db.scalar(
        select(User).where(User.id == user_id)
    )
    if user is not None:
        return user
    raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")


@router.get("/{user_id}/posts", response_model=list[PostResponse])
async def get_user_posts(user_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    user = await db.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
        
    posts = await db.scalars(
        select(Post).options(selectinload(Post.author))
        .where(Post.user_id == user_id)
        .order_by(Post.date_posted.desc()),
    )
    return posts.all()


@router.patch("/{user_id}", response_model=UserPrivate)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    user = await db.scalar(select(User).where(User.id == user_id))

    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, 
                            "User not found")

    if (
        user_update.username is not None 
        and user_update.username.lower() != user.username.lower()
    ):
        existing_user = await db.scalar(
            select(User)
            .where(func.lower(User.username) == user_update.username.lower()),
        )
        if existing_user:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, 
                                "Username already exists")
        
    if user_update.email is not None and user_update.email != user.email:
        existing_email = await db.scalar(
            select(User)
            .where(func.lower(User.email) == user_update.email.lower()),
        )
        if existing_email:
            raise HTTPException(status.HTTP_400_BAD_REQUEST,
                                "Email already registered")

    if user_update.username is not None:
        user.username = user_update.username
    if user_update.email is not None:
        user.email = user_update.email.lower()
    if user_update.image_file is not None:
        user.image_file = user_update.image_file

    await db.commit()
    await db.refresh(user)

    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().one_or_none()
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    await db.delete(user)
    await db.commit()