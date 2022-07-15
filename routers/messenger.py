import datetime

from jose import jwt
from fastapi.responses import RedirectResponse
from fastapi import APIRouter, Depends, Request, Cookie
from sqlalchemy import select, func, update, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.templating import Jinja2Templates
from config import SECRET_KEY, JWT_ALGORITHM
from messenger import Message, Dialog
from core import get_session, do_random_image, do_user_image
from user import User, get_current_user, user_availability

templates = Jinja2Templates(directory="data/templates")
router = APIRouter(prefix="/messenger")


@router.get('/dialog/{other_user_id}')
async def dialog(other_user_id: int,
                 request: Request,
                 session: AsyncSession = Depends(get_session),
                 current_user=Depends(get_current_user)):
    user = await user_availability(request.cookies.get('access_token', None), session)
    dialog_id = await session.execute(
        select(Dialog.id).where(or_(and_(Dialog.user == current_user.id,
                                         Dialog.other_user == other_user_id),
                                    and_(Dialog.user == other_user_id,
                                         Dialog.other_user == current_user.id))))
    dialog_id = dialog_id.scalar()

    user_dialog = await session.execute(select(User).where(User.id == other_user_id))
    user_dialog = user_dialog.scalar()
    if dialog_id:
        messages = await session.execute(select(Message).where(Message.dialog_id == dialog_id))
        messages = messages.scalars().all()[-31:]
        messages.reverse()
        response = templates.TemplateResponse("dialog.html", context={"request": request,
                                                                      "title": 'dialog',
                                                                      "current_user": user,
                                                                      'messages': messages,
                                                                      "other_user": user_dialog,
                                                                      "user": current_user})
    else:
        dialog = Dialog(user=current_user.id, other_user=other_user_id)
        session.add(dialog)
        await session.commit()
        await session.close()
        response = templates.TemplateResponse("dialog.html", context={"request": request,
                                                                      "title": 'dialog',
                                                                      "current_user": user,
                                                                      "other_user": user_dialog})
    return response


@router.get('/people')
async def people(request: Request,
                 session: AsyncSession = Depends(get_session),
                 current_user=Depends(get_current_user)):
    user = await user_availability(request.cookies.get('access_token', None), session)
    users_for_dialog = await session.execute(
        select(Dialog).where(or_(Dialog.user == current_user.id,
                                 Dialog.other_user == current_user.id)))
    users_for_dialog = users_for_dialog.scalars().all()
    users = []
    if users_for_dialog:
        for p in users_for_dialog:
            if p.user == current_user.id:
                users.append(p.other_user)
            else:
                users.append(p.user)
    users_t = []
    for u in users:
        us = await session.execute(select(User).where(User.id == u))
        us = us.scalar()
        users_t.append(us)
    response = templates.TemplateResponse("people.html", context={"request": request,
                                                                  "title": 'Люди...',
                                                                  "current_user": user,
                                                                  "people": users_t})
    return response


@router.post('/dialog/{other_user_id}')
async def post_dialog(other_user_id: int,
                      request: Request,
                      session: AsyncSession = Depends(get_session),
                      current_user=Depends(get_current_user)):
    data = await request.form()
    dialog_id = await session.execute(
        select(Dialog.id).where(or_(and_(Dialog.user == current_user.id,
                                         Dialog.other_user == other_user_id),
                                    and_(Dialog.user == other_user_id,
                                         Dialog.other_user == current_user.id))))
    dialog_id = int(dialog_id.scalar())
    if data.get("message"):
        message = Message(text=data.get("message"),
                          created_date=datetime.datetime.now(),
                          dialog_id=dialog_id,
                          user_who_sent_message=current_user.id,
                          user_for_whom_message=other_user_id)
        session.add(message)
        await session.commit()
        await session.close()
    return RedirectResponse(f"/messenger/dialog/{other_user_id}", status_code=302)


"""
@router.get('/show/{test_id}')
async def testik(test_id: int,
                 request: Request,
                 session: AsyncSession = Depends(get_session),
                 current_user=Depends(get_current_user)):
    testik = await session.execute(select(Test).where(Test.id == test_id))
    testik = testik.scalar()
    if not testik:
        return templates.TemplateResponse('server_response.html',
                                          {"request": request, "title": "ТЕСТИК!!!",
                                           'text': "Такого теста нет",
                                           'status': 1,
                                           'current_user': current_user})
    author_of_test = await session.execute(select(User).where(User.id == testik.author))
    author_of_test = author_of_test.scalar()
    questions_and_answers = {}
    q = await session.execute(
        select(Question).join(questions_to_test).join(Test).where(Test.id == test_id))
    q = q.scalars().all()
    for i in range(len(q)):
        new_dict = {'question': q[i].question,
                    'answers': []}
        q_id = q[i].id
        a = await session.execute(
            select(Answer).join(answers_to_question).join(Question).where(Question.id == q_id))
        a = a.scalars().all()
        for el in a:
            new_dict['answers'].append([el.answer])
        questions_and_answers[i] = new_dict
    response = templates.TemplateResponse("testik.html", context={"request": request,
                                                                  "title": 'ТЕСТИК!!!',
                                                                  'test_name': testik.test_name,
                                                                  'about_test': testik.about,
                                                                  'author': author_of_test,
                                                                  'date': testik.created_date,
                                                                  'img': testik.image,
                                                                  'questions_and_answers': questions_and_answers,
                                                                  'current_user': current_user,
                                                                  'test_id': test_id})
    return response"""
