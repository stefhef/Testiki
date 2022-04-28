from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.templating import Jinja2Templates
from core import get_session
from test import Test
from user import user_availability, get_current_user
from fastapi import APIRouter, Depends, Response, Request

templates = Jinja2Templates(directory="data/templates")
router = APIRouter(
    prefix="/user",
    tags=["user"]
)


@router.get("/profile")
async def read_users_me(request: Request,
                        current_user=Depends(get_current_user),
                        session: AsyncSession = Depends(get_session)):
    user = await user_availability(request.cookies.get('access_token', None), session)
    query = await session.execute(select(Test).where(Test.author == current_user.id))
    tests = query.scalars().all()

    return templates.TemplateResponse("profile.html", {"request": request,
                                                       "name": current_user.name,
                                                       "surname": current_user.surname,
                                                       "login": current_user.username,
                                                       "email": current_user.email,
                                                       "about": current_user.about,
                                                       "user_tests": tests,
                                                       'current_user': user})


@router.get("/me")
async def read_users_me(current_user=Depends(get_current_user)):
    if current_user.is_admin:
        return current_user
