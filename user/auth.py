from datetime import timedelta, datetime
from typing import Optional
from fastapi import Cookie
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from config import ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, JWT_ALGORITHM
from core.db import get_session
from user.models import User


class TokenData(BaseModel):
    email: Optional[str] = None


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password) if plain_password else False


def get_password_hash(password):
    return pwd_context.hash(password)


async def get_user(email: str, session: AsyncSession) -> Optional[User]:
    query = await session.execute(select(User).where(User.email == email))
    user = query.scalars().first()
    return user


async def authenticate_user(email: str, password: str, session: AsyncSession) -> Optional[User]:
    user = await get_user(email, session)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


async def get_current_user(access_token: Optional[str] = Cookie(None),
                           session: AsyncSession = Depends(get_session)):
    """Возвращает пользователя если он авторизован и ошибку в противном случае"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not access_token:
        raise credentials_exception
    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        email: str = payload.get("email")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = await get_user(token_data.email, session)
    if user is None:
        raise credentials_exception
    return user


def create_jwt_token(data: dict,
                     expires_delta: Optional[timedelta] = None,
                     verify_exp: bool = True) -> str:
    """Формирование JWT токена"""
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


async def create_access_token_user(user: User, session: AsyncSession) -> str:
    """Формирование токена доступа"""
    jwt_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    query = await session.execute(select(User)
                                  .where(User.id == user.id))
    user = query.scalars().first()
    jwt_data = {"email": user.email}
    jwt_token = create_jwt_token(data=jwt_data, expires_delta=jwt_token_expires)
    return jwt_token


async def user_availability(access_token, session: AsyncSession):
    try:
        return await get_current_user(access_token, session)
    except HTTPException:
        return None
