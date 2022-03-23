import datetime
from typing import Optional

import sqlalchemy
from fastapi_users import models
from pydantic import EmailStr

from core.db import metadata

user = sqlalchemy.Table(
    'users',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column('username', sqlalchemy.String, index=True),
    sqlalchemy.Column('name', sqlalchemy.String, nullable=True),
    sqlalchemy.Column('surname', sqlalchemy.String, nullable=True),
    sqlalchemy.Column('about', sqlalchemy.String, nullable=True),
    sqlalchemy.Column('email', sqlalchemy.String, index=True, unique=True),
    sqlalchemy.Column('password', sqlalchemy.String),
    sqlalchemy.Column('created_date', sqlalchemy.DateTime, default=datetime.datetime.now),
    sqlalchemy.Column('is_superuser', sqlalchemy.Boolean, default=False),
)


# class User(models.BaseUser):
#     id: int
#     name: str
#     surname: str
#     about: Optional[str]
#     email: EmailStr
#     password: str
#     created_date: datetime.datetime = datetime.datetime.now()
#     is_superuser: bool = False


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

#
# class UserDB(User, models.BaseUserDB):
#     pass
#     # id: int
#     # name: str
#     # surname: str
#     # about: Optional[str]
#     # email: EmailStr
#     # password: str
#     # created_date: datetime.datetime = datetime.datetime.now()
#     # is_superuser: bool = False
