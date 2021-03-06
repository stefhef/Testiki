import datetime
import sqlalchemy
from sqlalchemy import orm
from core.db import Base

questions_to_test = sqlalchemy.Table('questions_to_test',
                                     Base.metadata,
                                     sqlalchemy.Column('questions', sqlalchemy.Integer,
                                                       sqlalchemy.ForeignKey('questions.id')),
                                     sqlalchemy.Column('tests', sqlalchemy.Integer,
                                                       sqlalchemy.ForeignKey('tests.id')))

answers_to_question = sqlalchemy.Table('answers_to_question',
                                       Base.metadata,
                                       sqlalchemy.Column('answer', sqlalchemy.Integer,
                                                         sqlalchemy.ForeignKey('answers.id')),
                                       sqlalchemy.Column('question', sqlalchemy.Integer,
                                                         sqlalchemy.ForeignKey('questions.id')))


class Test(Base):
    __tablename__ = 'tests'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    test_name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    about = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    author = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    questions = orm.relation("Question",
                             secondary='questions_to_test',
                             backref="tests")
    image = sqlalchemy.Column(sqlalchemy.BLOB, nullable=False)

    def __repr__(self):
        return f"ID:{self.id} Название теста: {self.test_name} Про тест:{self.about} ID автора: {self.author} Время создания: {self.created_date}"


class Question(Base):
    __tablename__ = 'questions'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    question = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    id_author = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    answers = orm.relation("Answer",
                           secondary='answers_to_question',
                           backref="questions")

    def __repr__(self):
        return f"ID:{self.id} Текст вопроса:{self.question} ID автора: {self.id_author}"


class Answer(Base):
    __tablename__ = 'answers'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    answer = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    is_true = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False, default=False)
    id_author = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)

    def __repr__(self):
        return f"ID:{self.id} Текст ответа:{self.answer} ID автора: {self.id_author} Правильный: {self.is_true}"
