import datetime
from typing import Optional
from jose import jwt
from fastapi.responses import RedirectResponse
from fastapi import APIRouter, Depends, Request, Cookie
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.templating import Jinja2Templates
from config import SECRET_KEY, JWT_ALGORITHM
from test import Test, questions_to_test, Question, Answer, answers_to_question
from core import get_session, do_random_image, do_user_image
from user import User, get_current_user

templates = Jinja2Templates(directory="data/templates")
router = APIRouter(prefix="/testik")


@router.get('/show/{test_id}')
async def testik(test_id: int,
                 request: Request,
                 session: AsyncSession = Depends(get_session),
                 current_user=Depends(get_current_user)):
    testik = await session.execute(select(Test).where(Test.id == test_id))
    testik = testik.scalar()
    if not testik:
        return templates.TemplateResponse('server_response.html',
                                          {"request": request, "title": "ТЕСТИК!!!",
                                           'text': "Такого теста нет",
                                           'status': 1,
                                           'current_user': current_user})
    author_of_test = await session.execute(select(User).where(User.id == testik.author))
    author_of_test = author_of_test.scalar()
    questions_and_answers = {}
    q = await session.execute(
        select(Question).join(questions_to_test).join(Test).where(Test.id == test_id))
    q = q.scalars().all()
    for i in range(len(q)):
        new_dict = {'question': q[i].question,
                    'answers': []}
        q_id = q[i].id
        a = await session.execute(
            select(Answer).join(answers_to_question).join(Question).where(Question.id == q_id))
        a = a.scalars().all()
        for el in a:
            new_dict['answers'].append([el.answer])
        questions_and_answers[i] = new_dict
    response = templates.TemplateResponse("testik.html", context={"request": request,
                                                                  "title": 'ТЕСТИК!!!',
                                                                  'test_name': testik.test_name,
                                                                  'about_test': testik.about,
                                                                  'author': author_of_test,
                                                                  'date': testik.created_date,
                                                                  'img': testik.image,
                                                                  'questions_and_answers': questions_and_answers,
                                                                  'current_user': current_user,
                                                                  'test_id': test_id})
    return response


@router.post('/show/{test_id}')
async def result_testik(test_id: int,
                        request: Request,
                        session: AsyncSession = Depends(get_session),
                        current_user=Depends(get_current_user)):
    query = await session.execute(select(Test).where(Test.id == test_id))
    testik = query.scalars().first()

    q = await session.execute(
        select(Question).join(questions_to_test).join(Test).where(Test.id == test_id))
    q = q.scalars().all()

    all_answers = []
    questions_and_answers = {}
    author_of_test = await session.execute(select(User).where(User.id == testik.author))
    author_of_test = author_of_test.scalar()
    for i in range(len(q)):
        new_dict = {'question': q[i].question,
                    'answers': []}
        q_id = q[i].id
        a = await session.execute(
            select(Answer).join(answers_to_question).join(Question).where(Question.id == q_id))
        a = a.scalars().all()
        for el in a:
            all_answers.append((el.answer, el.is_true))
            new_dict['answers'].append((el.answer, el.is_true))
        questions_and_answers[i] = new_dict

    true_answers = list(filter(lambda x: x[1] is True, all_answers))

    data = await request.form()

    user_answers = []
    for key, value in data.items():
        if 'answer' in key:
            user_answers.append(value)
    for key, value in questions_and_answers.items():
        for n, elem in enumerate(value['answers']):
            try:
                if elem[0] == user_answers[key]:
                    questions_and_answers[key]['answers'][n] = (elem[0], elem[1], True)
                else:
                    questions_and_answers[key]['answers'][n] = (elem[0], elem[1], False)
            except IndexError:
                response = templates.TemplateResponse("testik.html", context={"request": request,
                                                                              "title": 'ТЕСТИК!!!',
                                                                              'test_name': testik.test_name,
                                                                              "warning": "Вы ответили не на все вопросики(",
                                                                              'about_test': testik.about,
                                                                              'author': author_of_test,
                                                                              'date': testik.created_date,
                                                                              'img': testik.image,
                                                                              'questions_and_answers': questions_and_answers,
                                                                              'current_user': current_user,
                                                                              'test_id': test_id})
                return response
    count = 0
    for true_a, user_a in zip(true_answers, user_answers):
        if true_a[0] == user_a:
            count += 1

    response = templates.TemplateResponse("testik_result.html", context={"request": request,
                                                                         "title": 'ТЕСТИК!!! Результатики)',
                                                                         'test_name': testik.test_name,
                                                                         'about_test': testik.about,
                                                                         'author': author_of_test,
                                                                         'date': testik.created_date,
                                                                         'img': testik.image,
                                                                         'questions_and_answers':
                                                                             questions_and_answers,
                                                                         'current_user': current_user,
                                                                         'test_id': test_id,
                                                                         'end': f'Правильных ответов {count}/{len(true_answers)}, вы справились с тестом на {round(count / len(true_answers) * 100, 2)}%'})

    return response


@router.get("/make_test")
async def make_test(request: Request,
                    current_user=Depends(get_current_user)):
    return templates.TemplateResponse('make_test_first.html', context={'request': request,
                                                                       'title': 'Создание теста',
                                                                       'current_user': current_user})


@router.post('/make_test')
async def make_test_p(request: Request,
                    current_user=Depends(get_current_user)):
    data = await request.form()
    if not all(data.values()):
        return templates.TemplateResponse('make_test_first.html',
                                          context={'request': request, 'title': 'Создание тестиков',
                                                   "error": "Не всё введено"})
    try:
        answ_and_quest = templates.TemplateResponse('make_test_second.html', context={'request': request,
                                                                                      'title': 'Создание тестиков',
                                                                                      'n_questions': int(
                                                                                          data['questions']),
                                                                                      'n_answers': int(
                                                                                          data['answers']),
                                                                                      "current_user": current_user})
    except ValueError:
        return templates.TemplateResponse('make_test_first.html',
                                          context={'request': request, 'title': 'Создание тестиков',
                                                   "error": "Вы зачем пишите буковки туда, куда надо писать число?... Мы в шоке просто с вас..."})

    answ_and_quest.set_cookie('questions', data['questions'], httponly=True)
    answ_and_quest.set_cookie('answers', data['answers'], httponly=True)
    answ_and_quest.set_cookie('test_name',
                              jwt.encode({'test_name': data['test_name']}, SECRET_KEY,
                                         algorithm=JWT_ALGORITHM),
                              httponly=True)
    answ_and_quest.set_cookie('about', jwt.encode({'about': data['about_test']}, SECRET_KEY,
                                                  algorithm=JWT_ALGORITHM),
                              httponly=True)
    return answ_and_quest


@router.post('/obr')
async def obr(request: Request,
              session: AsyncSession = Depends(get_session),
              current_user=Depends(get_current_user),
              questions: Optional[int] = Cookie(None),
              answers: Optional[int] = Cookie(None),
              test_name: Optional[str] = Cookie(None),
              about: Optional[str] = Cookie(None)):
    if questions == 0 or answers == 0:
        return templates.TemplateResponse('make_test_second.html', context={'request': request,
                                                                            'text': 'Эммммммм',
                                                                            'status': 0,
                                                                            'current_user': current_user})
    data = await request.form()
    a = await data["file"].read()
    if not a:
        a = do_random_image(800, 600)
    else:
        a = do_user_image((800, 600), a)

    if not all(data.values()):
        return templates.TemplateResponse('make_test_second.html', context={'request': request,
                                                                            'title': 'Не всё введено',
                                                                            'n_questions': questions,
                                                                            'n_answers': answers,
                                                                            'current_user': current_user})

    test_name = jwt.decode(test_name, SECRET_KEY, algorithms=[JWT_ALGORITHM]).get('test_name')
    about = jwt.decode(about, SECRET_KEY, algorithms=[JWT_ALGORITHM]).get('about')
    test = Test(author=current_user.id,
                test_name=test_name,
                about=about,
                created_date=datetime.datetime.now(),
                image=a)

    first = True
    is_t_count = 0
    for key, value in data.items():
        if 'question' in key:
            if not first:
                test.questions.append(question)
                session.add(question)
            first = False
            question = Question(question=value, id_author=current_user.id)
        elif 'answer' in key:
            answer = Answer(answer=value, is_true=False, id_author=current_user.id)
            question.answers.append(answer)
            session.add(answer)
        elif 'is_true' in key:
            is_t_count += 1
            req = await session.execute(select(func.max(Answer.id))
                                        .where(Answer.id_author == current_user.id))
            id_t = req.scalars().first()
            await session.execute(update(Answer).where(Answer.id == id_t).values(is_true=True))

    if questions != is_t_count:
        return templates.TemplateResponse('make_test_second.html', context={'request': request,
                                                                            'title': 'Не всё введено',
                                                                            'n_questions': questions,
                                                                            'n_answers': answers,
                                                                            'current_user': current_user,
                                                                            "error": "Не всё введено"})

    test.questions.append(question)
    session.add(question)
    session.add(test)
    await session.commit()
    await session.close()

    response = RedirectResponse('/', status_code=302)
    response.set_cookie('answers', '0')
    response.set_cookie('questions', '0')
    return response
