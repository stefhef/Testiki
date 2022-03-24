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
from config import SECRET_KEY
from routers import auth_router

app = FastAPI()

app.include_router(auth_router)

app.mount("/static", StaticFiles(directory="data/static"), name="static")

templates = Jinja2Templates(directory="data/templates")


@app.on_event("startup")
async def startup():
    await init_db()


@app.get("/about")
async def say_hello(request: Request):
    return templates.TemplateResponse("about.html", {"request": request, "title": 'Главная страница'})


@app.get("/")
async def root(request: Request, session: AsyncSession = Depends(get_session)):
    return templates.TemplateResponse("main.html", {"request": request, "title": 'Главная страница'})


if __name__ == "__main__":
    uvicorn.run('main:app', log_level="info", )
