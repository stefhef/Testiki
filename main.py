import uvicorn as uvicorn
from fastapi import FastAPI, Request, Depends, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from core.db import db
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_login import LoginManager  # Loginmanager Class
from fastapi_login.exceptions import InvalidCredentialsException
from user.models import user as user_model

import asyncio

app = FastAPI()

SECRET = "secret-key"
manager = LoginManager(SECRET, token_url="/auth/login", use_cookie=True)
manager.cookie_name = "some-name"

app.mount("/static", StaticFiles(directory="data/static"), name="static")

templates = Jinja2Templates(directory="data/templates")


@app.on_event("startup")
async def startup():
    await db.connect()


@app.on_event("shutdown")
async def shutdown():
    await db.disconnect()

@manager.user_loader
async def load_user(username: str):
    query = user_model.select()
    users = await db.fetch_one(query)
    return users





@app.get("/about")
async def say_hello(request: Request):
    return templates.TemplateResponse("about.html", {"request": request, "title": 'Главная страница'})


@app.get("/")
async def root(request: Request):
    if request.user.is_authenticated:
        return {"message": f"Hello hello"}
    return {"message": f"Hello"}
    # return templates.TemplateResponse("main.html", {"request": request, "title": 'Главная страница'})


if __name__ == "__main__":
    asyncio.run(load_user('abc'))
    # uvicorn.run('main:app', log_level="info", )
