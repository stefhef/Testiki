import datetime
from fastapi.responses import RedirectResponse
from fastapi import APIRouter, Depends, Request
from sqlalchemy import select, or_, and_, update
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.templating import Jinja2Templates
from messenger import Message, Dialog
from core import get_session
from user import User, get_current_user, user_availability

templates = Jinja2Templates(directory="data/templates")
router = APIRouter(prefix="/messenger")


@router.get('/dialog/{other_user_id}')
async def dialog(other_user_id: int,
                 request: Request,
                 session: AsyncSession = Depends(get_session),
                 current_user=Depends(get_current_user)):
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
        response = templates.TemplateResponse("dialog.html", context={"request": request,
                                                                      "title": 'dialog',
                                                                      'messages': messages,
                                                                      "other_user": user_dialog,
                                                                      "current_user": current_user})
    else:
        dialog = Dialog(user=current_user.id, other_user=other_user_id)
        session.add(dialog)
        await session.commit()
        await session.close()
        response = templates.TemplateResponse("dialog.html", context={"request": request,
                                                                      "title": 'dialog',
                                                                      "current_user": current_user,
                                                                      "other_user": user_dialog})
    response.set_cookie("user_id", current_user.id)
    await session.execute(update(Message).where(
        and_(Message.dialog_id == dialog_id, Message.user_for_whom_message == current_user.id)).values(
        {Message.status: True}))
    await session.commit()
    await session.close()
    return response


@router.get('/people')
async def people(request: Request,
                 session: AsyncSession = Depends(get_session),
                 current_user=Depends(get_current_user)):
    users_for_dialog = await session.execute(
        select(Dialog).where(or_(Dialog.user == current_user.id,
                                 Dialog.other_user == current_user.id)))
    users_for_dialog = users_for_dialog.scalars().all()
    users = []
    if users_for_dialog:
        for p in users_for_dialog:
            if p.user == current_user.id:
                users.append((p.other_user, p.id))
            else:
                users.append((p.user, p.id))
    for i, (u, id_d) in enumerate(users):
        mess = await session.execute(select(Message).where(
            and_(Message.dialog_id == id_d, Message.status == 0, Message.user_for_whom_message != u)))
        mess = mess.scalars().all()
        users[i] = (u, len(mess))
    users_t = []
    for u, n in users:
        us = await session.execute(select(User).where(User.id == u))
        us = us.scalar()
        users_t.append((us, n))
    response = templates.TemplateResponse("people.html", context={"request": request,
                                                                  "title": 'Люди...',
                                                                  "current_user": current_user,
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


@router.get("/data")
async def data(id: int,
               session: AsyncSession = Depends(get_session)):
    user = await session.execute(select(User).where(User.id == id))
    data = user.scalar()
    return data.name + data.surname, data.image.__str__()[2:-1]


@router.post('/send_message')
async def send_message(msg,
                       from_id,
                       to_id,
                       session: AsyncSession = Depends(get_session)):
    dialog_id = await session.execute(
        select(Dialog.id).where(or_(and_(Dialog.user == from_id,
                                         Dialog.other_user == to_id),
                                    and_(Dialog.user == to_id,
                                         Dialog.other_user == from_id))))
    dialog_id = int(dialog_id.scalar())
    message = Message(text=msg,
                      created_date=datetime.datetime.now(),
                      dialog_id=dialog_id,
                      user_who_sent_message=from_id,
                      user_for_whom_message=to_id)
    session.add(message)
    await session.commit()
    await session.close()
    return "OK"
