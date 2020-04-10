import random

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from qanta import create_session, Question, router, all_qanta_ids


app = FastAPI()
app.include_router(router, prefix='/api/qanta/v1')
app.mount("/static", StaticFiles(directory="static"), name="static")


templates = Jinja2Templates(directory="templates")

@app.get("/")
async def read_random_question(request: Request):
    with create_session() as session:
        qanta_id = random.choice(all_qanta_ids)
        question = session.query(Question).filter_by(qanta_id=qanta_id).first().to_dict()
    return templates.TemplateResponse("question.html.jinja2", {'request': request, **question})


@app.get("/question/{qanta_id}")
async def read_question(request: Request, qanta_id: int):
    with create_session() as session:
        question = session.query(Question).filter_by(qanta_id=qanta_id).first().to_dict()
    return templates.TemplateResponse("question.html.jinja2", {'request': request, **question})