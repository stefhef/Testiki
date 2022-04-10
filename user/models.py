import datetime
from enum import IntEnum
from typing import Optional

import sqlalchemy
from pydantic import EmailStr
from sqlalchemy_serializer import SerializerMixin
from core.db import Base
from pydantic import BaseModel
from sqlalchemy.orm import relationship


class UserStatus(IntEnum):
    ACTIVE: int = 1
    BLOCKED: int = 2
    UNDEFINED: int = -1


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
    status = sqlalchemy.Column(sqlalchemy.Enum(UserStatus), default=UserStatus.UNDEFINED)

    refresh_token = relationship("RefreshToken", back_populates="user")

    def __repr__(self):
        return f'<User> {self.id} {self.name} {self.surname} {self.email}'

    # def set_password(self, password):
    #     self.hashed_password = generate_password_hash(password)
    #
    # def check_password(self, password):
    #     return check_password_hash(self.hashed_password, password)


class UserModel(BaseModel):
    id: int

    name: str
    surname: str
    about: str
    email: EmailStr
    password: str
    created_date: datetime.datetime
    is_admin: bool



class UserCreate(BaseModel):
    id: int
    name: str
    surname: str
    about: Optional[str]
    email: EmailStr
    password: str
    created_date: datetime.datetime = datetime.datetime.now()
    is_superuser: bool = False
