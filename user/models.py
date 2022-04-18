import datetime
from enum import IntEnum
import sqlalchemy
from core.db import Base
from sqlalchemy.orm import relationship


class UserStatus(IntEnum):
    ACTIVE: int = 1
    BLOCKED: int = 2
    UNDEFINED: int = -1


class User(Base):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    surname = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    username = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    about = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String, index=True, unique=True, nullable=False)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    is_admin = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False, default=False)
    status = sqlalchemy.Column(sqlalchemy.Enum(UserStatus), default=UserStatus.UNDEFINED)
    tests = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    #  в tests - строку где id тестов пользователя через пробел

    refresh_token = relationship("RefreshToken", back_populates="user")

    def __repr__(self):
        return f'<User> {self.id} {self.name} {self.surname} {self.email}'
