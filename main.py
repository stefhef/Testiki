import uvicorn as uvicorn
from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from core.db import init_db, get_session
from sqlalchemy.ext.asyncio import AsyncSession
from routers import auth_router
from user.auth import get_current_user

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
async def root(request: Request,
               session: AsyncSession = Depends(get_session)):
    return templates.TemplateResponse("main.html", {"request": request, "title": 'Главная страница'})


@app.get("/users/me/")
async def read_users_me(current_user=Depends(get_current_user)):
    if current_user.is_admin:
        return current_user


@app.get("/profile")
async def read_users_me(request: Request, current_user=Depends(get_current_user)):
    return templates.TemplateResponse("me.html", {"request": request,
                                                  "name": current_user.name,
                                                  "surname": current_user.surname,
                                                  "login": current_user.username,
                                                  "email": current_user.email,
                                                  "about": current_user.about})
    #  TODO: add list of tests of current user + image


if __name__ == "__main__":
    uvicorn.run('main:app', log_level="info", reload=True)
