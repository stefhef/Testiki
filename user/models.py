import datetime
from typing import Optional

from fastapi_users import models
from pydantic import EmailStr



class User(models.BaseUser):
    id: int
    name: str
    surname: str
    about: Optional[str]
    email: EmailStr
    password: str
    created_date: datetime.datetime = datetime.datetime.now()
    is_superuser: bool = False


class UserCreate(models.BaseUserCreate):
    id: int
    name: str
    surname: str
    about: Optional[str]
    email: EmailStr
    password: str
    created_date: datetime.datetime = datetime.datetime.now()
    is_superuser: bool = False


class UserUpdate(models.BaseUserUpdate):
    id: int
    name: str
    surname: str
    about: Optional[str]
    email: EmailStr
    password: str
    created_date: datetime.datetime = datetime.datetime.now()
    is_superuser: bool = False


class UserDB(User, models.BaseUserDB):
    pass
    # id: int
    # name: str
    # surname: str
    # about: Optional[str]
    # email: EmailStr
    # password: str
    # created_date: datetime.datetime = datetime.datetime.now()
    # is_superuser: bool = False