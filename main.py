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
    return current_user


if __name__ == "__main__":
    uvicorn.run('main:app', log_level="info", reload=True)
