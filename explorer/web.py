import random

import toml
import uvicorn

from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


from explorer.database import SessionLocal, Question, get_db, CuriosityDbDialog
from explorer.qanta.api import qanta_app, get_all_qanta_ids, get_html_qanta_question
from explorer.curiosity.api import curiosity_app


with open("data.toml") as f:
    data = toml.load(f)


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/qanta", qanta_app)
app.mount("/curiosity", curiosity_app)


templates = Jinja2Templates(directory="templates")


@app.get("/")
async def home(request: Request, db: SessionLocal = Depends(get_db)):
    return templates.TemplateResponse(
        "index.html.jinja2", {"request": request, "datasets": data["datasets"].values()}
    )


@app.get("/dataset/qanta")
async def qanta_dataset(request: Request, db: SessionLocal = Depends(get_db)):
    # TODO: make this a real homepage
    qanta_id = random.choice(get_all_qanta_ids(db))
    return get_html_qanta_question(db, request, qanta_id)


@app.get("/dataset/curiosity")
async def curiosity_dataset(request: Request, db: SessionLocal = Depends(get_db)):
    return templates.TemplateResponse(
        "curiosity/landing.html.jinja2", {"request": request}
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
