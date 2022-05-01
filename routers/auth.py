from typing import Optional
from pydantic import BaseModel
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import APIRouter, Depends, Response, Request
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.templating import Jinja2Templates
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
    response = RedirectResponse('/')
    response.delete_cookie("access_token")
    return response


@router.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    """Форма для входа"""
    return templates.TemplateResponse('login.html', context={'request': request, 'title': 'Авторизация'})


@router.post("/login", response_class=HTMLResponse)
async def login_p(request: Request,
                  session: AsyncSession = Depends(get_session)):
    """Обработчик входа"""
    data = await request.form()

    user = await session.execute(select(User).where(User.username == data['username']))
    user = user.scalars().first()
    if not user:
        return templates.TemplateResponse('login.html',
                                          context={'request': request, 'title': 'Вход',
                                                   "error": "Логин или пароль неверны"})

    if not verify_password(data.get('password', None), user.hashed_password):
        return templates.TemplateResponse('login.html',
                                          context={'request': request, 'title': 'Вход',
                                                   "error": "Логин или пароль неверны"})

    jwt_access_token = await create_access_token_user(user, session)
    result = templates.TemplateResponse('main.html',
                                        context={'request': request, 'title': 'Вошли', 'current_user': user})
    result.set_cookie("access_token", jwt_access_token, httponly=True)
    return result


@router.get("/test")
async def test_auth(current_user=Depends(get_current_user)):
    """Проверка авторизации"""
    return current_user


@router.get("/register", response_class=HTMLResponse)
async def register_p(request: Request):
    return templates.TemplateResponse('register.html', context={'request': request, 'title': 'Авторизация'})


@router.get("/lost_password")
async def lost_password(request: Request):
    return templates.TemplateResponse("server_response.html", context={'request': request, 'title': 'Хехехе',
                                                                       'text': 'Ну сами виноваты',
                                                                       'status': 1})


@router.post("/register", response_class=HTMLResponse)
async def register_p(request: Request,
                     session: AsyncSession = Depends(get_session)):
    data = await request.form()
    res = await session.execute(select(User).where(User.email == data['email']))
    if res.scalars().first():
        return templates.TemplateResponse('register.html',
                                          context={'request': request, 'title': 'Регистрация',
                                                   "error": "Почта занята"})
    res = await session.execute(select(User).where(User.username == data['username']))
    if res.scalars().first():
        return templates.TemplateResponse('register.html',
                                          context={'request': request, 'title': 'Регистрация',
                                                   "error": "Логин занят"})
    dct = dict()
    for key, value in data.items():
        dct[key] = value
    dct['hashed_password'] = get_password_hash(dct['hashed_password'])
    await session.execute(insert(User).values(**dct))
    await session.commit()
    await session.close()
    return RedirectResponse('/auth/login')
