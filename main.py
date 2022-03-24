import uvicorn as uvicorn
from fastapi import FastAPI, Request, Depends, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from core.db import init_db, get_session
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi.security import OAuth2PasswordRequestForm
from fastapi_login import LoginManager  # Loginmanager Class
from fastapi_login.exceptions import InvalidCredentialsException
from user.models import User
from sqlalchemy import select

import asyncio

app = FastAPI()

SECRET = "secret-key"
manager = LoginManager(SECRET, token_url="/auth/login", use_cookie=True)
manager.cookie_name = "some-name"

app.mount("/static", StaticFiles(directory="data/static"), name="static")

templates = Jinja2Templates(directory="data/templates")


@app.on_event("startup")
async def startup():
    await init_db()


@manager.user_loader
async def load_user(username: str, session: AsyncSession) -> User:
    # .begin()
    query = await session.execute(select(User).where(User.username == username))
    user = query.scalars().first()
    return user


@app.get("/about")
async def say_hello(request: Request):
    return templates.TemplateResponse("about.html", {"request": request, "title": 'Главная страница'})


@app.get("/")
async def root(request: Request, session: AsyncSession = Depends(get_session)):
    return {"message": f"Hello"}
    # return templates.TemplateResponse("main.html", {"request": request, "title": 'Главная страница'})


@app.post("/auth/login")
def login(data: OAuth2PasswordRequestForm = Depends()):
    username = data.username
    password = data.password
    user = load_user(username)
    if not user:
        raise InvalidCredentialsException
    elif password != user['password']:
        raise InvalidCredentialsException
    access_token = manager.create_access_token(
        data={"sub": username}
    )
    resp = RedirectResponse(url="/private", status_code=status.HTTP_302_FOUND)
    manager.set_cookie(resp, access_token)
    return resp


@app.get('/login')
def login(request: Request, session: AsyncSession):
    pass


if __name__ == "__main__":
    uvicorn.run('main:app', log_level="info", )
