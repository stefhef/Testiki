import aiohttp as aiohttp
import uvicorn as uvicorn
from fastapi import FastAPI, Request, Depends
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
import asyncio
from core.db import init_db, get_session
from sqlalchemy.ext.asyncio import AsyncSession
from routers import auth_router
from user.auth import get_current_user
from core.vk import vk_send_message
from user.models import User

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


@app.get("/complaint")
async def complaint(request: Request):
    return templates.TemplateResponse("complaint.html", {"request": request, "title": 'Жалоба('})


@app.post("/complaint")
async def p_complaint(request: Request,
                      session: AsyncSession = Depends(get_session)):
    data = await request.form()
    if not data.get('text', None):
        return templates.TemplateResponse("server_response.html", {"request": request, "title": 'Сообщение сервера',
                                                                   "status": 0, "text": "Не все данные введены"})
    query = await session.execute(select(User).where(User.is_admin == True, User.vk_id != None))
    users = query.scalars().all()
    users_ids = list(map(lambda x: x.vk_id, users))
    if users_ids:
        asyncio.create_task(vk_send_message(f"Пожаловались: {data.get('text', None)}", users_ids))
    return templates.TemplateResponse("server_response.html", {"request": request, "title": 'Сообщение сервера',
                                                               "status": 1, "text": "Ваша жалоба принята"})


@app.get("/insult")
async def complaint(request: Request,
                    session: AsyncSession = Depends(get_session)):
    async with aiohttp.ClientSession() as session_h:
        async with session_h.get("https://evilinsult.com/generate_insult.php?lang=ru&type=json") as resp:
            json = await resp.json()
            text = json["insult"]
        query = await session.execute(select(User).where(User.is_admin == True, User.vk_id != None))
        users = query.scalars().all()
        users_ids = list(map(lambda x: x.vk_id, users))
    if users_ids:
        asyncio.create_task(vk_send_message(f"Обзываются(( {text}", users_ids))
    return templates.TemplateResponse("server_response.html", {"request": request, "title": 'Сообщение сервера',
                                                               "status": 1, "text": "Поздравляем! Вы обозвали администраторов"})


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
                                                  "about": current_user.about,
                                                  "user_tests": current_user.tests})
    #  TODO: add list of tests of current user + image


if __name__ == "__main__":
    uvicorn.run('main:app', log_level="info", reload=True)
