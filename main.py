from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

app.mount("/static", StaticFiles(directory="data/static"), name="static")

templates = Jinja2Templates(directory="data/templates")


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.get("/about")
async def say_hello(request: Request):
    return templates.TemplateResponse("about.html", {"request": request, "title": 'Главная страница'})


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("main.html", {"request": request, "title": 'Главная страница'})
