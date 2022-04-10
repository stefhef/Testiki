from typing import Optional

import uvicorn as uvicorn
from fastapi import FastAPI, Request, Depends, Cookie, HTTPException, Response
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette import status

from core.db import init_db, get_session
from sqlalchemy.ext.asyncio import AsyncSession
from routers import auth_router
from routers.auth import Token
from user.auth import authenticate_user, create_access_token_user, create_refresh_token_user, get_current_user, get_user
from user.models import User, UserModel

app = FastAPI()

app.include_router(auth_router)

app.mount("/static", StaticFiles(directory="data/static"), name="static")

templates = Jinja2Templates(directory="data/templates")


@app.on_event("startup")
async def startup():
    await init_db()


@app.post("/token", response_model=Token)
async def login_for_access_token(response: Response,
                                 form_data: OAuth2PasswordRequestForm = Depends(),
                                 refresh_token: Optional[str] = Cookie(None),
                                 session: AsyncSession = Depends(get_session)):
    user = await authenticate_user(form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    jwt_access_token = await create_access_token_user(user, session)
    jwt_refresh_token = await create_refresh_token_user(user, session, refresh_token)
    response.set_cookie("refresh_token", jwt_refresh_token, httponly=True)
    return Token(access_token=jwt_access_token)


@app.get("/about")
async def say_hello(request: Request):
    return templates.TemplateResponse("about.html", {"request": request, "title": 'Главная страница'})


@app.get("/")
async def root(request: Request, session: AsyncSession = Depends(get_session)):
    user = await get_user('Степан_Владиславович', session)
    print(user)
    return templates.TemplateResponse("main.html", {"request": request, "title": 'Главная страница'})


@app.get("/users/me/")
async def read_users_me(current_user=Depends(get_current_user)):
    return current_user


if __name__ == "__main__":
    uvicorn.run('main:app', log_level="info", )
