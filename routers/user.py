from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.templating import Jinja2Templates
from core import get_session, do_user_image, do_random_image
from test import Test
from user import get_current_user, User
from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse

templates = Jinja2Templates(directory="data/templates")
router = APIRouter(
    prefix="/user",
    tags=["user"]
)


@router.get("/profile")
async def read_users_me(request: Request,
                        current_user=Depends(get_current_user),
                        session: AsyncSession = Depends(get_session)):
    query = await session.execute(select(Test).where(Test.author == current_user.id))
    tests = query.scalars().all()
    image = str(current_user.image)[2:-1]
    return templates.TemplateResponse("profile.html", {"request": request,
                                                       "name": current_user.name,
                                                       "surname": current_user.surname,
                                                       "username": current_user.username,
                                                       "email": current_user.email,
                                                       "about": current_user.about,
                                                       "image": image,
                                                       "user_tests": tests,
                                                       'current_user': current_user})


@router.get("/edit_profile")
async def edit_profile(request: Request,
                       current_user=Depends(get_current_user)):
    image = str(current_user.image)[2:-1]
    return templates.TemplateResponse("edit_profile.html", {"request": request,
                                                            "name": current_user.name,
                                                            "surname": current_user.surname,
                                                            "username": current_user.username,
                                                            "email": current_user.email,
                                                            "about": current_user.about,
                                                            "image": image,
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
            image = str(current_user.image)[2:-1]
            return templates.TemplateResponse("edit_profile.html", {"request": request,
                                                                    "name": current_user.name,
                                                                    "surname": current_user.surname,
                                                                    "username": current_user.username,
                                                                    "email": current_user.email,
                                                                    "about": current_user.about,
                                                                    "image": image,
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
