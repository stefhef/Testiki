from datetime import timedelta, datetime
from typing import Optional

from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from config import ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, JWT_ALGORITHM
from core.db import get_session
from core.refresh_token import RefreshToken

from user.models import User


class TokenData(BaseModel):
    username: Optional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def create_access_token_user(user: User, session: AsyncSession) -> str:
    jwt_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    query = await session.execute(select(User)
                                  .where(User.id == user.id))
    user = query.scalars().first()
    jwt_data = {"vk_id": user.vk_id, "is_admin": bool(user.admin), "is_teacher": bool(user.teacher)}
    jwt_token = create_jwt_token(data=jwt_data, expires_delta=jwt_token_expires)
    return jwt_token


# TODO: async session context
async def create_refresh_token_user(user: User,
                                    session: AsyncSession,
                                    refresh_token: Optional[str] = None) -> str:
    jwt_token = create_jwt_token(data={"username": user.username}, verify_exp=False)
    new_refresh_token = RefreshToken(token=jwt_token, user=user)
    if refresh_token:
        query = await session.execute(select(RefreshToken).where(RefreshToken.token == refresh_token,
                                                                 RefreshToken.user == user))
        old_refresh_token = query.scalars().first()
        if old_refresh_token:
            await session.delete(old_refresh_token)
            await session.commit()
    session.add(new_refresh_token)
    await session.commit()
    return jwt_token


def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password) if plain_password else False


def get_password_hash(password):
    return pwd_context.hash(password)


# TODO: async context
async def get_user(username: str, session: AsyncSession) -> Optional[User]:
    query = await session.execute(select(User).where(User.username == username))
    user = query.scalars().first()
    return user


async def authenticate_user(username: str, password: str, session: AsyncSession) -> Optional[User]:
    user = await get_user(username, session)
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user


def create_jwt_token(data: dict,
                     expires_delta: Optional[timedelta] = None,
                     verify_exp: bool = True) -> str:
    to_encode = data.copy()
    if verify_exp:
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    else:
        expire = datetime.utcnow()
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


async def get_current_user(session: AsyncSession, token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        username: str = payload.get("username")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = await get_user(token_data.username, session)
    if user is None:
        raise credentials_exception
    return user


# Не знаю зачем...........
"""
async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.status != UserStatus.ACTIVE:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user
"""
