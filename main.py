import uvicorn as uvicorn
from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from core.db import create_db_and_tables
from user.models import UserDB
from user.logic import auth_backend, current_active_user, fastapi_users
from core.auth import middleware

app = FastAPI(middleware=middleware)

app.mount("/static", StaticFiles(directory="data/static"), name="static")

templates = Jinja2Templates(directory="data/templates", auto_reload=True)


@app.get("/about")
async def say_hello(request: Request):
    return templates.TemplateResponse("about.html", {"request": request, "title": 'Главная страница'})


@app.get("/")
async def root(request: Request):
    if request.user.is_authenticated:
        return {"message": f"Hello hello"}
    return {"message": f"Hello"}
    # return templates.TemplateResponse("main.html", {"request": request, "title": 'Главная страница'})


app.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"]
)
app.include_router(fastapi_users.get_register_router(), prefix="/auth", tags=["auth"])
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_verify_router(),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(fastapi_users.get_users_router(), prefix="/users", tags=["users"])


@app.get("/authenticated-route")
async def authenticated_route(user: UserDB = Depends(current_active_user)):
    return {"message": f"Hello {user.email}!"}


@app.on_event("startup")
async def on_startup():
    # Not needed if you setup a migration system like Alembic
    await create_db_and_tables()


if __name__ == "__main__":
    uvicorn.run('main:app', log_level="info", )
