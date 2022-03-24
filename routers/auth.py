import json
from typing import Optional, Any
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import ValidationError
from fastapi.responses import HTMLResponse
from fastapi import APIRouter, status, HTTPException, Cookie, Depends, Response, Request, Form
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from fastapi.templating import Jinja2Templates
from user.models import UserModel
from core.db import get_session
from user.models import User
from user.auth import get_password_hash, create_access_token_user, create_refresh_token_user, get_current_active_user

templates = Jinja2Templates(directory="data/templates")
router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)


@router.get("/logout")
async def logout(response: Response):
    response.delete_cookie("refresh_token")
    return {"status": "Ok"}


@router.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse('login.html', context={'request': request, 'title': 'Авторизация'})


@router.post("/login", response_class=HTMLResponse)
async def login(request: Request,
                session: AsyncSession = Depends(get_session),
                username: str = Form(...),
                password: str = Form(...)):
    print(username, password)
    return templates.TemplateResponse('login.html', context={'request': request, 'title': 'Done'})
