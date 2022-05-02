from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.templating import Jinja2Templates
from core import get_session, do_user_image, do_random_image
from test import Test
from user import get_current_user, User, user_availability
from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse

templates = Jinja2Templates(directory="data/templates")
router = APIRouter(
    prefix="/user",
    tags=["user"]
)


@router.get("/profile")
async def profile_me(request: Request,
                     current_user=Depends(get_current_user),
                     session: AsyncSession = Depends(get_session)):
    query = await session.execute(select(Test).where(Test.author == current_user.id))
    tests = query.scalars().all()
    return templates.TemplateResponse("profile.html", {"request": request,
                                                       "title": "Профиль",
                                                       "name": current_user.name,
                                                       "surname": current_user.surname,
                                                       "username": current_user.username,
                                                       "email": current_user.email,
                                                       "about": current_user.about,
                                                       "image": current_user.image,
                                                       "user_tests": tests,
                                                       'current_user': current_user,
                                                       "me": True})


@router.get("/profile/{profile_id}")
async def read_users_me(request: Request,
                        profile_id: int,
                        session: AsyncSession = Depends(get_session)):
    site_user = await user_availability(request.cookies.get('access_token', None), session)
    query = await session.execute(select(User).where(User.id == profile_id))
    user = query.scalar()
    if not user:
        return templates.TemplateResponse("server_response.html",
                                          {"request": request, "title": "Профиль",
                                           'text': "Пользователь не существует(",
                                           'status': 0,
                                           'current_user': site_user})
    query = await session.execute(select(Test).where(Test.author == user.id))
    tests = query.scalars().all()
    return templates.TemplateResponse("profile.html", {"request": request,
                                                       "title": "Профиль",
                                                       "name": user.name,
                                                       "surname": user.surname,
                                                       "username": user.username,
                                                       "email": user.email,
                                                       "about": user.about,
                                                       "image": user.image,
                                                       "user_tests": tests,
                                                       'current_user': site_user})


@router.get("/edit_profile")
async def edit_profile(request: Request,
                       current_user=Depends(get_current_user)):
    return templates.TemplateResponse("edit_profile.html", {"request": request,
                                                            "title": "Редактирование профиля",
                                                            "name": current_user.name,
                                                            "surname": current_user.surname,
                                                            "username": current_user.username,
                                                            "email": current_user.email,
                                                            "about": current_user.about,
                                                            "image": current_user.image,
                                                            'current_user': current_user})


@router.post('/edit_profile')
async def edit_profile_p(request: Request,
                         current_user: User = Depends(get_current_user),
                         session: AsyncSession = Depends(get_session)):
    data = await request.form()

    if data.get("username") != current_user.username:
        query = await session.execute(select(User).where(User.username == data.get("username")))
        user = query.scalar()
        if user:
            return templates.TemplateResponse("edit_profile.html", {"request": request,
                                                                    "title": "Редактирование профиля",
                                                                    "name": current_user.name,
                                                                    "surname": current_user.surname,
                                                                    "username": current_user.username,
                                                                    "email": current_user.email,
                                                                    "about": current_user.about,
                                                                    "image": current_user.image,
                                                                    'current_user': current_user,
                                                                    "error": "Такой логин занят!"})

    if not data.get("delete", None):
        photo = await data.get("photo").read()

        if not photo:
            photo = current_user.image
        else:
            photo = do_user_image((800, 600), photo)
    else:
        photo = do_random_image(800, 600)
    dct = {}
    for key, value in data.items():
        if key == "photo":
            dct["image"] = photo
        elif key == 'delete':
            continue
        else:
            dct[key] = value
    await session.execute(update(User).where(User.id == current_user.id).values(**dct))
    await session.commit()
    await session.close()
    return RedirectResponse("/user/profile", status_code=302)


@router.get("/me")
async def read_users_me(current_user=Depends(get_current_user)):
    if current_user.is_admin:
        return current_user
