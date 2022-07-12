import os

import aiohttp as aiohttp
import uvicorn as uvicorn
from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select, or_
import asyncio
from core import init_db, get_session, vk_send_message
from sqlalchemy.ext.asyncio import AsyncSession
from routers import auth_router, user_router, testiki_router, messenger_router
from test import Test
from user import get_current_user, user_availability, User

app = FastAPI()
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(testiki_router)
app.include_router(messenger_router)
app.mount("/static", StaticFiles(directory="data/static"), name="static")
templates = Jinja2Templates(directory="data/templates")


@app.on_event("startup")
async def startup():
    await init_db()


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request,
                                 exc: StarletteHTTPException
                                 ):
    """Обработчик исключений HTTP"""
    session = get_session()
    sess = await session.__anext__()
    user = await user_availability(request.cookies.get('access_token', None), sess)
    if exc.status_code == 401:
        return templates.TemplateResponse('server_response.html',
                                          {"request": request, "title": exc.status_code,
                                           'text': f"Не авторизованы ай-ай",
                                           'status': 0,
                                           'current_user': user})
    elif exc.status_code == 404:
        return templates.TemplateResponse('server_response.html',
                                          {"request": request, "title": exc.status_code,
                                           'text': f"Страница не найдена((",
                                           'status': 0,
                                           'current_user': user})
    else:
        return templates.TemplateResponse('server_response.html',
                                          {"request": request, "title": exc.status_code,
                                           'text': f"Ошибочка(("
                                                   f"{exc.status_code}",
                                           'status': 0,
                                           'current_user': user})


@app.get("/about")
async def say_hello(request: Request,
                    session: AsyncSession = Depends(get_session)):
    user = await user_availability(request.cookies.get('access_token', None), session)
    return templates.TemplateResponse("about.html",
                                      {"request": request, "title": 'О нас', 'current_user': user})


@app.get("/")
async def root(request: Request,
               session: AsyncSession = Depends(get_session)):
    user = await user_availability(request.cookies.get('access_token', None), session)
    query = await session.execute(select(Test))
    tests = query.scalars().all()
    await session.close()
    for test in tests:
        test.image = str(test.image)[2:-1]
        if len(test.test_name) > 30:
            test.test_name = f'{test.test_name[:30]}..'
        if len(test.about) > 100:
            test.about = f'{test.about[:100]}..'
    return templates.TemplateResponse("main.html",
                                      {"request": request, "title": 'Главная страница',
                                       'current_user': user,
                                       'tests': tests})


@app.get("/complaint")
async def complaint(request: Request,
                    session: AsyncSession = Depends(get_session)):
    user = await user_availability(request.cookies.get('access_token', None), session)
    return templates.TemplateResponse("complaint.html", {"request": request, "title": 'Жалоба(',
                                                         'current_user': user})


@app.post("/complaint")
async def p_complaint(request: Request,
                      session: AsyncSession = Depends(get_session)):
    user = await user_availability(request.cookies.get('access_token', None), session)
    data = await request.form()
    if not data.get('text', None):
        return templates.TemplateResponse("server_response.html",
                                          {"request": request, "title": 'Сообщение сервера',
                                           "status": 0, "text": "Не все данные введены",
                                           'current_user': user})
    query = await session.execute(select(User).where(User.is_admin == True, User.vk_id != None))
    users = query.scalars().all()
    users_ids = list(map(lambda x: x.vk_id, users))
    if users_ids:
        asyncio.create_task(vk_send_message(f"Пожаловались: {data.get('text', None)}", users_ids))
    return templates.TemplateResponse("server_response.html",
                                      {"request": request, "title": 'Сообщение сервера',
                                       "status": 1, "text": "Ваша жалоба принята",
                                       'current_user': user})


@app.get("/insult")
async def complaint(request: Request,
                    current_user=Depends(get_current_user),
                    session: AsyncSession = Depends(get_session)):
    async with aiohttp.ClientSession() as session_h:
        async with session_h.get(
                "https://evilinsult.com/generate_insult.php?lang=ru&type=json") as resp:
            json = await resp.json()
            text = json["insult"]
        query = await session.execute(select(User).where(User.is_admin == True, User.vk_id != None))
        users = query.scalars().all()
        users_ids = list(map(lambda x: x.vk_id, users))
    if users_ids:
        asyncio.create_task(
            vk_send_message(f"{current_user.username} обзывается(( {text}", users_ids))
    return templates.TemplateResponse("server_response.html", {"request": request,
                                                               "title": 'Сообщение сервера',
                                                               "status": 1,
                                                               "text": "Поздравляем! Вы обозвали администраторов",
                                                               'current_user': current_user})


@app.post('/search_test')
async def search_test(request: Request,
                      session: AsyncSession = Depends(get_session),
                      current_user=Depends(get_current_user)):
    data = await request.form()
    text = data['search']
    user = await user_availability(request.cookies.get('access_token', None), session)
    tests = await session.execute(select(Test).where(Test.test_name.like(f'%{text}%')))
    tests = tests.scalars().all()
    authors = await session.execute(select(User).where(or_(User.username.like(f'%{text}%'),
                                                           User.name.like(f'%{text}%'),
                                                           User.surname.like(f'%{text}%'))))
    authors = authors.scalars().all()
    for test in tests:
        test.image = str(test.image)[2:-1]
    if tests or authors:
        return templates.TemplateResponse("main.html",
                                          {"request": request, "title": text,
                                           'current_user': user,
                                           'tests': tests,
                                           'authors': authors})
    else:
        return templates.TemplateResponse("main.html",
                                          {"request": request, "title": text,
                                           'current_user': user,
                                           'warning': 'Ничего не найдено(('})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run('main:app', log_level="info", reload=True, host="127.0.0.1", port=port)
