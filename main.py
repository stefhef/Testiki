import datetime
from typing import Optional

import aiohttp as aiohttp
import uvicorn as uvicorn
from fastapi import FastAPI, Request, Depends, Form, Cookie
from fastapi.responses import RedirectResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select, insert, func, update
import asyncio
from fastapi.templating import Jinja2Templates
from core.db import init_db, get_session
from sqlalchemy.ext.asyncio import AsyncSession
from routers import auth_router
from test import Question, models
from test.models import Test, Answer
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


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc: StarletteHTTPException):
    """Обработчик исключений HTTP"""
    if exc.status_code == 401:
        return templates.TemplateResponse('server_response.html', {"request": request, "title": exc.status_code,
                                                                   'text': f"Не авторизованы ай-ай",
                                                                   'status': 0})
    elif exc.status_code == 404:
        return templates.TemplateResponse('server_response.html', {"request": request, "title": exc.status_code,
                                                                   'text': f"Страница не найдена((",
                                                                   'status': 0})
    else:
        return templates.TemplateResponse('server_response.html', {"request": request, "title": exc.status_code,
                                                                   'text': f"Ошибочка(("
                                                                           f"{exc.status_code}",
                                                                   'status': 0})


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
                    current_user=Depends(get_current_user),
                    session: AsyncSession = Depends(get_session)):
    async with aiohttp.ClientSession() as session_h:
        async with session_h.get("https://evilinsult.com/generate_insult.php?lang=ru&type=json") as resp:
            json = await resp.json()
            text = json["insult"]
        query = await session.execute(select(User).where(User.is_admin == True, User.vk_id != None))
        users = query.scalars().all()
        users_ids = list(map(lambda x: x.vk_id, users))
    if users_ids:
        asyncio.create_task(vk_send_message(f"{current_user.username} обзывается(( {text}", users_ids))
    return templates.TemplateResponse("server_response.html", {"request": request, "title": 'Сообщение сервера',
                                                               "status": 1,
                                                               "text": "Поздравляем! Вы обозвали администраторов"})


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


@app.get("/db_ks")
async def db_ks(request: Request,
                session: AsyncSession = Depends(get_session)):
    return templates.TemplateResponse('test_f.html', context={'request': request, 'title': 'dtht'})


@app.post('/db_ks')
async def db_ks(request: Request,
                session: AsyncSession = Depends(get_session),
                current_user=Depends(get_current_user)):
    data = await request.form()
    if not all(data.values()):
        return templates.TemplateResponse('test_f.html', context={'request': request, 'title': 'АЙ-ай-ай'})
    answ_and_quest = templates.TemplateResponse('test_2.html', context={'request': request, 'title': 'dtht',
                                                                        'n_questions': int(data['questions']),
                                                                        'n_answers': int(data['answers'])})
    answ_and_quest.set_cookie('questions', data['questions'], httponly=True)
    answ_and_quest.set_cookie('answers', data['answers'], httponly=True)

    dct = {'test_name': data['test_name'],
           'about': data['about_test'],
           'author': current_user.id,
           'created_date': datetime.datetime.now(),
           'is_hidden': False}
    print(dct)
    await session.execute(insert(Test).values(**dct))
    await session.commit()
    await session.close()

    return answ_and_quest


@app.post('/obr')
async def obr(request: Request,
              session: AsyncSession = Depends(get_session),
              current_user=Depends(get_current_user),
              questions: Optional[int] = Cookie(None),
              answers: Optional[int] = Cookie(None)):
    q, a = questions, answers

    if q == 0 or a == 0:
        return templates.TemplateResponse('server_response.html', context={'request': request,
                                                                           'text': 'Эммммммм',
                                                                           'status': 0})
    data = await request.form()
    if not all(data.values()):
        return templates.TemplateResponse('test_2.html', context={'request': request,
                                                                  'title': 'Не всё введено',
                                                                  'n_questions': q,
                                                                  'n_answers': a})

    for key, value in data.items():
        if 'question' in key:
            await session.execute(insert(Question).values(question=value))
        elif 'answer' in key:
            answer = Answer(answer=value, is_true=False, id_author=current_user.id, id_users_now=None)
            session.add(answer)
            """await session.execute(insert(Answer).values(**{'answer': value,
                                                           'is_true': False,
                                                           'id_author': current_user.id}))"""
        elif 'is_true' in key:
            req = await session.execute(select(func.max(Answer.id)).where(Answer.id_author == current_user.id))
            id_t = req.scalars().first()
            await session.execute(update(Answer).where(Answer.id == id_t).values(is_true=True))

        await session.commit()
        await session.close()

    response = templates.TemplateResponse("main.html", {"request": request, "title": 'Главная страница'})
    response.set_cookie('answers', '0')
    response.set_cookie('questions', '0')
    return response


if __name__ == "__main__":
    uvicorn.run('main:app', log_level="info", reload=True)
