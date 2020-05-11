import random

from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


from qanta.database import SessionLocal, Question, get_db, PlayEvent


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


templates = Jinja2Templates(directory="templates")
CACHED_QANTA_IDS = []


def get_all_qanta_ids(db):
    if len(CACHED_QANTA_IDS) == 0:
        all_qanta_ids = [r[0] for r in db.query(Question.qanta_id).all()]
        CACHED_QANTA_IDS.extend(all_qanta_ids)
    return CACHED_QANTA_IDS


def get_html_question(db, request, qanta_id: int, n: int = 15):
    question = db.query(Question).filter_by(qanta_id=qanta_id).first().to_dict()
    records = (
        db.query(PlayEvent).filter_by(qanta_id=qanta_id).order_by(PlayEvent.date).all()
    )
    n_records = len(records)
    sample = [r.to_dict() for r in records[:n]]
    return templates.TemplateResponse(
        "question.html.jinja2",
        {"request": request, "plays": sample, "n_plays": n_records, **question},
    )


@app.get("/")
async def home(request: Request, db: SessionLocal = Depends(get_db)):
    qanta_id = random.choice(get_all_qanta_ids(db))
    return get_html_question(db, request, qanta_id)


@app.get("/qanta/question/random")
async def read_random_question(request: Request, db: SessionLocal = Depends(get_db)):
    qanta_id = random.choice(get_all_qanta_ids(db))
    return get_html_question(db, request, qanta_id)


@app.get("/qanta/question/{qanta_id}")
async def read_question(
    request: Request, qanta_id: int, db: SessionLocal = Depends(get_db)
):
    return get_html_question(db, request, qanta_id)


@app.get("/api/qanta/v1/random")
def get_random_question(db: SessionLocal = Depends(get_db)):
    qanta_id = random.choice(get_all_qanta_ids(db))
    question = db.query(Question).filter_by(qanta_id=qanta_id).first()
    return question.to_dict()


@app.get("/api/qanta/v1/{qanta_id}")
def get_question(qanta_id: int, db: SessionLocal = Depends(get_db)):
    question = db.query(Question).filter_by(qanta_id=qanta_id).first()
    return question.to_dict()
