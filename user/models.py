import datetime
from typing import Optional

import sqlalchemy
from pydantic import EmailStr
from sqlalchemy_serializer import SerializerMixin
from core.db import Base
from pydantic import BaseModel


# from core.db import metadata

# user = sqlalchemy.Table(
#     'users',
#     metadata,
#     sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
#     sqlalchemy.Column('username', sqlalchemy.String, index=True),
#     sqlalchemy.Column('name', sqlalchemy.String, nullable=True),
#     sqlalchemy.Column('surname', sqlalchemy.String, nullable=True),
#     sqlalchemy.Column('about', sqlalchemy.String, nullable=True),
#     sqlalchemy.Column('email', sqlalchemy.String, index=True, unique=True),
#     sqlalchemy.Column('password', sqlalchemy.String),
#     sqlalchemy.Column('created_date', sqlalchemy.DateTime, default=datetime.datetime.now),
#     sqlalchemy.Column('is_superuser', sqlalchemy.Boolean, default=False),
# )


class User(Base, SerializerMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    surname = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    username = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    about = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String, index=True, unique=True, nullable=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    is_admin = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False, default=False)

    def __repr__(self):
        return f'<User> {self.id} {self.name} {self.surname} {self.email}'

    # def set_password(self, password):
    #     self.hashed_password = generate_password_hash(password)
    #
    # def check_password(self, password):
    #     return check_password_hash(self.hashed_password, password)


# class User(models.BaseUser):
#     id: int
#     name: str
#     surname: str
#     about: Optional[str]
#     email: EmailStr
#     password: str
#     created_date: datetime.datetime = datetime.datetime.now()
#     is_superuser: bool = False


class UserCreate(BaseModel):
    id: int
    name: str
    surname: str
    about: Optional[str]
    email: EmailStr
    password: str
    created_date: datetime.datetime = datetime.datetime.now()
    is_superuser: bool = False


class UserUpdate(BaseModel):
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
