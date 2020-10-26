from typing import Optional
import random
import math

from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates

from explorer.database import SessionLocal, get_db, CuriosityDbDialog
from explorer.curiosity.wiki_db import CuriosityStore
from explorer.curiosity.data import CuriosityDialog

CACHED_CURIOSITY_IDS = []
CACHED_CURIOSITY_TOPICS = []
fact_lookup = CuriosityStore("data/curiosity/wiki_sql.sqlite.db").get_fact_lookup()

curiosity_app = FastAPI()
templates = Jinja2Templates(directory="templates")


def get_curiosity_topics(db: SessionLocal):
    if len(CACHED_CURIOSITY_TOPICS) == 0:
        topics = db.query(CuriosityDbDialog.topic).distinct().all()
        for t in topics:
            if isinstance(t, str):
                CACHED_CURIOSITY_TOPICS.append(t)
            else:
                CACHED_CURIOSITY_TOPICS.append(t[0])

        CACHED_CURIOSITY_TOPICS.extend(topics)
    return CACHED_CURIOSITY_TOPICS


def get_html_dialog(db, request: Request, dialog_id: int):
    dialog = db.query(CuriosityDbDialog).filter_by(dialog_id=dialog_id).first()
    if dialog is None:
        return templates.TemplateResponse(
            "missing.html.jinja2",
            {"request": request, "data_id": dialog_id, "data_name": "Curiosity Dialog"},
            status_code=404,
        )
    data = CuriosityDialog.parse_raw(dialog.data)
    dialog_facts = {}
    for msg in data.messages:
        for f in msg.facts:
            dialog_facts[f.fid] = fact_lookup[f.fid]

    return templates.TemplateResponse(
        "curiosity/dialog.html.jinja2",
        {"request": request, "dialog": data, "facts": dialog_facts},
    )


def get_all_curiosity_ids(db):
    if len(CACHED_CURIOSITY_IDS) == 0:
        all_curiosity_ids = [r[0] for r in db.query(CuriosityDbDialog.dialog_id).all()]
        CACHED_CURIOSITY_IDS.extend(all_curiosity_ids)
    return CACHED_CURIOSITY_IDS


@curiosity_app.get("/dialog/random")
async def read_random_dialog(request: Request, db: SessionLocal = Depends(get_db)):
    dialog_id = random.choice(get_all_curiosity_ids(db))
    return get_html_dialog(db, request, dialog_id)


@curiosity_app.get("/dialog/{dialog_id}")
async def read_dialog(
    request: Request, dialog_id: int, db: SessionLocal = Depends(get_db)
):
    return get_html_dialog(db, request, dialog_id)


@curiosity_app.get("/dialog/topic/{topic}")
async def read_dialogs_by_topic(
    request: Request, topic: str, db: SessionLocal = Depends(get_db)
):
    # pylint: disable=unused-argument
    topic_dialogs = db.query(CuriosityDbDialog).filter_by(topic=topic).all()
    n = len(topic_dialogs)
    return templates.TemplateResponse(
        "curiosity/topics.html.jinja2",
        {"request": request, "dialogs": topic_dialogs, "n": n, "topic": topic},
    )


@curiosity_app.get("/dialogs")
async def get_dialogs(
    request: Request,
    topic: Optional[str] = None,
    limit: int = 10,
    page: int = 1,
    db: SessionLocal = Depends(get_db),
):
    # pylint: disable=unused-argument
    if topic is None:
        dialogs = db.query(CuriosityDbDialog).limit(limit).offset((page - 1) * limit)
        total = db.query(CuriosityDbDialog).count()
    else:
        dialogs = (
            db.query(CuriosityDbDialog)
            .filter_by(topic=topic)
            .limit(limit)
            .offset((page - 1) * limit)
        )
        total = db.query(CuriosityDbDialog).filter_by(topic=topic).count()
    total_pages = math.ceil(total / limit)
    return {
        "dialogs": [CuriosityDialog.parse_raw(d.data) for d in dialogs],
        "n_dialogs": total,
        "n_pages": total_pages,
        "page": page,
        "topic": topic,
    }


@curiosity_app.get("/topics")
async def get_topics(request: Request, db: SessionLocal = Depends(get_db)):
    # pylint: disable=unused-argument
    topics = get_curiosity_topics(db)
    return {"topics": topics}
