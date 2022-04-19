from typing import Optional
from pydantic import BaseModel
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import APIRouter, status, HTTPException, Depends, Response, Request, Form, Cookie
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import joinedload
from user.auth import get_password_hash, verify_password, create_access_token_user, \
    get_current_user
from core.db import get_session
from user.models import User

templates = Jinja2Templates(directory="data/templates")
router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)


class TokenData(BaseModel):
    username: Optional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str = "Bearer"


@router.get("/logout")
async def logout(response: Response):
    response.delete_cookie("refresh_token")
    return {"status": "Ok"}


@router.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    """Форма для входа"""
    return templates.TemplateResponse('login.html', context={'request': request, 'title': 'Авторизация'})


@router.post("/login", response_class=HTMLResponse)
async def login_p(request: Request,
                  session: AsyncSession = Depends(get_session)):
    """Обработчик входа"""
    data = await request.form()
    if not all(data):
        return templates.TemplateResponse('login.html', context={'request': request, 'title': 'Не всё введено'})

    user = await session.execute(select(User).where(User.email == data['email']))
    user = user.scalars().first()
    if not user:
        return templates.TemplateResponse('login.html',
                                          context={'request': request, 'title': 'Такого пользователя нет'})

    if not verify_password(data.get('password', None), user.hashed_password):
        return templates.TemplateResponse('login.html',
                                          context={'request': request, 'title': 'Пароль неверный'})

    jwt_access_token = await create_access_token_user(user, session)
    result = templates.TemplateResponse('login.html',
                                        context={'request': request, 'title': 'Вошли'})
    result.set_cookie("access_token", jwt_access_token, httponly=True)
    return result


@router.get("/test")
async def test_auth(current_user=Depends(get_current_user)):
    """Проверка авторизации"""
    return current_user


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

