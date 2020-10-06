import random

from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates

from explorer.database import SessionLocal, Question, get_db

qanta_app = FastAPI()
templates = Jinja2Templates(directory="templates")

CACHED_QANTA_IDS = []


def get_all_qanta_ids(db):
    if len(CACHED_QANTA_IDS) == 0:
        all_qanta_ids = [r[0] for r in db.query(Question.qanta_id).all()]
        CACHED_QANTA_IDS.extend(all_qanta_ids)
    return CACHED_QANTA_IDS


def get_html_qanta_question(db, request, qanta_id: int, n: int = 15):
    question = db.query(Question).filter_by(qanta_id=qanta_id).first()
    question_dict = question.to_dict(include_buzzes=True)
    records = sorted(
        [r for r in question.plays if r.result != "prompt"], key=lambda r: r.date
    )
    n_records = len(records)
    sample = [r.to_dict() for r in records[:n]]
    return templates.TemplateResponse(
        "question.html.jinja2",
        {"request": request, "plays": sample, "n_plays": n_records, **question_dict},
    )


@qanta_app.get("/question/random")
async def read_random_question(request: Request, db: SessionLocal = Depends(get_db)):
    qanta_id = random.choice(get_all_qanta_ids(db))
    return get_html_qanta_question(db, request, qanta_id)


@qanta_app.get("/question/{qanta_id}")
async def read_question(
    request: Request, qanta_id: int, db: SessionLocal = Depends(get_db)
):
    return get_html_qanta_question(db, request, qanta_id)


@qanta_app.get("/api/qanta/v1/random")
def get_random_question(db: SessionLocal = Depends(get_db)):
    qanta_id = random.choice(get_all_qanta_ids(db))
    question = db.query(Question).filter_by(qanta_id=qanta_id).first()
    return question.to_dict()


@qanta_app.get("/api/qanta/v1/{qanta_id}")
def get_question(qanta_id: int, db: SessionLocal = Depends(get_db)):
    question = db.query(Question).filter_by(qanta_id=qanta_id).first()
    return question.to_dict()
