from datetime import timedelta
from typing import Optional
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import BaseModel
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import APIRouter, status, HTTPException, Depends, Response, Request, Form, Cookie
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import joinedload

from config import ACCESS_TOKEN_EXPIRE_MINUTES
from user.auth import get_password_hash, verify_password, authenticate_user, create_access_token_user, \
    create_refresh_token_user
from core.db import get_session
from user.models import User
from core.refresh_token import RefreshToken

templates = Jinja2Templates(directory="data/templates")
router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class TokenData(BaseModel):
    username: Optional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str


@router.get("/logout")
async def logout(response: Response):
    response.delete_cookie("refresh_token")
    return {"status": "Ok"}


@router.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse('login.html', context={'request': request, 'title': 'Авторизация'})


@router.post("/login", response_class=HTMLResponse, )
async def login_p(request: Request,
                  refresh_token: Optional[str] = Cookie(None),
                  session: AsyncSession = Depends(get_session)):
    data = await request.form()
    if not all(data.values()):
        return templates.TemplateResponse('login.html', context={'request': request, 'title': 'Не всё введено'})

    user = await session.execute(select(User).where(User.email == data['email']))
    user = user.scalars().first()
    if not user:
        return templates.TemplateResponse('login.html',
                                          context={'request': request, 'title': 'Такого пользователя нет'})

    if not verify_password(data['password'], user.hashed_password):
        return templates.TemplateResponse('login.html',
                                          context={'request': request, 'title': 'Пароль неверный'})
    jwt_access_token = await create_access_token_user(user, session)
    jwt_refresh_token = await create_refresh_token_user(user, session, refresh_token)
    request.set_cookie("refresh_token", jwt_refresh_token, httponly=True)
    return RedirectResponse('/')


@router.get("/register", response_class=HTMLResponse)
async def register_p(request: Request,
                     session: AsyncSession = Depends(get_session)):
    return templates.TemplateResponse('register.html', context={'request': request, 'title': 'Авторизация'})


@router.post("/register", response_class=HTMLResponse)
async def register_p(request: Request,
                     session: AsyncSession = Depends(get_session)):
    data = await request.form()
    if not all(data.values()):
        return templates.TemplateResponse('register.html',
                                          context={'request': request, 'title': 'Не все данные введены'})
    res = await session.execute(select(User).where(User.email == data['email']))
    if res.scalars().first():
        return templates.TemplateResponse('register.html',
                                          context={'request': request, 'title': 'Почта занята'})
    res = await session.execute(select(User).where(User.username == data['username']))
    if res.scalars().first():
        return templates.TemplateResponse('register.html',
                                          context={'request': request, 'title': 'Логин занят'})
    dct = dict()
    for key, value in data.items():
        dct[key] = value
    dct['hashed_password'] = get_password_hash(dct['hashed_password'])
    await session.execute(insert(User).values(**dct))
    await session.commit()
    await session.close()
    return RedirectResponse('/auth/login')
    # return templates.TemplateResponse('register.html', context={'request': request, 'title': 'Done'})


@router.get("/refresh_token", response_model=Token)
async def refresh(response: Response,
                  refresh_token: Optional[str] = Cookie(None),
                  session: AsyncSession = Depends(get_session)):
    query = await session.execute(select(RefreshToken)
                                  .where(RefreshToken.token == refresh_token)
                                  .options(joinedload(RefreshToken.user)))
    db_refresh_token = query.scalars().first()
    if db_refresh_token:
        db_user = db_refresh_token.user
        jwt_access_token = await create_access_token_user(db_user, session)
        jwt_refresh_token = await create_refresh_token_user(db_user, session, refresh_token)
        response.set_cookie("refresh_token", jwt_refresh_token, httponly=True)
        return Token(access_token=jwt_access_token)
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bad refresh token. Need to reauthorize.")
