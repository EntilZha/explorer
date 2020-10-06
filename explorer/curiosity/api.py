import random

from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates

from explorer.database import SessionLocal, Question, get_db
from explorer.database import SessionLocal, get_db, CuriosityDbDialog
from explorer.curiosity.wiki_db import CuriosityStore
from explorer.curiosity.data import CuriosityDialog

CACHED_CURIOSITY_IDS = []
fact_lookup = CuriosityStore("data/curiosity/wiki_sql.sqlite.db").get_fact_lookup()

curiosity_app = FastAPI()
templates = Jinja2Templates(directory="templates")


def get_html_dialog(db, request, dialog_id: int):
    dialog = db.query(CuriosityDbDialog).filter_by(dialog_id=dialog_id).first()
    data = CuriosityDialog.parse_raw(dialog.data)
    return templates.TemplateResponse(
        "curiosity.html.jinja2", {"request": request, "dialog": data},
    )


def get_all_curiosity_ids(db):
    if len(CACHED_CURIOSITY_IDS) == 0:
        all_curiosity_ids = [r[0] for r in db.query(CuriosityDbDialog.dialog_id).all()]
        CACHED_CURIOSITY_IDS.extend(all_curiosity_ids)
    return CACHED_CURIOSITY_IDS


@curiosity_app.get("/dialog/random")
async def read_random_question(request: Request, db: SessionLocal = Depends(get_db)):
    dialog_id = random.choice(get_all_curiosity_ids(db))
    return get_html_dialog(db, request, dialog_id)


@curiosity_app.get("/dialog/{dialog_id}")
async def read_question(
    request: Request, dialog_id: int, db: SessionLocal = Depends(get_db)
):
    return get_html_dialog(db, request, dialog_id)
