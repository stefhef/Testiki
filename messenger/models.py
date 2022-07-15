import datetime
import sqlalchemy
from sqlalchemy import orm
from core.db import Base

"""message_to_user = sqlalchemy.Table('message_to_user',
                                   Base.metadata,
                                   sqlalchemy.Column('message', sqlalchemy.Integer,
                                                     sqlalchemy.ForeignKey('messages.id')),
                                   sqlalchemy.Column('user', sqlalchemy.Integer,
                                                     sqlalchemy.ForeignKey('users.id')))

message_to_other_user = sqlalchemy.Table('message_to_other_user',
                                         Base.metadata,
                                         sqlalchemy.Column('message', sqlalchemy.Integer,
                                                           sqlalchemy.ForeignKey('messages.id')),
                                         sqlalchemy.Column('other_user', sqlalchemy.Integer,
                                                           sqlalchemy.ForeignKey('users.id')))"""


class Message(Base):
    __tablename__ = 'messages'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    text = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    # other = sqlalchemy.Column
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    status = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    dialog_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    user_who_sent_message = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    user_for_whom_message = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)

    def __repr__(self):
        return f"ID:{self.id} Текст сообщения: {self.text}" \
               f"ID автора: {self.user_who_sent_message}" \
               f"ID получателя {self.user_who_sent_message} Время создания: {self.created_date}"


class Dialog(Base):
    __tablename__ = 'dialogs'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    other_user = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)

    def __repr__(self):
        return f"ID:{self.id} User:{self.user} Other_user:{self.other_user09o}"
