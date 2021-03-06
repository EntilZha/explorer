from typing import List
import json
from contextlib import contextmanager

import pandas as pd
from tqdm import tqdm

from pedroai.math import to_precision
from pedroai.io import read_json

from sqlalchemy import (
    Column,
    ForeignKey,
    Float,
    Integer,
    String,
    Boolean,
    DateTime,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, scoped_session
from sqlalchemy.exc import OperationalError

from explorer.log import get_logger
from explorer.curiosity.data import CuriosityDialog


Base = declarative_base()
engine = create_engine(
    "sqlite:///data/qanta_viewer.sqlite3", connect_args={"check_same_thread": False}
)
SessionLocal = scoped_session(
    sessionmaker(bind=engine, autoflush=False, autocommit=False)
)


log = get_logger(__name__)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context() -> SessionLocal:
    session = SessionLocal()
    yield session
    session.close()


class Question(Base):
    __tablename__ = "questions"
    qanta_id = Column(Integer, primary_key=True)
    text = Column(String)
    first_sentence = Column(String)
    tokenizations = Column(String)
    answer = Column(String)
    page = Column(String)
    fold = Column(String)
    gameplay = Column(Boolean)
    category = Column(String)
    subcategory = Column(String)
    tournament = Column(String)
    difficulty = Column(String)
    year = Column(Integer)
    proto_id = Column(Integer)
    qdb_id = Column(Integer)
    dataset = Column(String)
    plays = relationship("PlayEvent")

    def to_dict(self, include_buzzes=False, max_buzzes=5):
        return {
            "qanta_id": self.qanta_id,
            "text": self.text,
            "tokenizations": json.loads(self.tokenizations),
            "answer": self.answer,
            "page": self.page,
            "fold": self.fold,
            "gameplay": self.gameplay,
            "category": self.category,
            "subcategory": self.subcategory,
            "tournament": self.tournament,
            "difficulty": self.difficulty,
            "year": self.year,
            "proto_id": self.proto_id,
            "qdb_id": self.proto_id,
            "dataset": self.dataset,
            "text_with_buzzes": self.text_with_buzzes(max_buzzes=max_buzzes)
            if include_buzzes
            else None,
        }

    def text_with_buzzes(self, max_buzzes: int = 5):
        filtered_events = []
        seen_players = set()
        for event in self.plays:
            if event.user_id in seen_players:
                continue
            filtered_events.append(event)
            seen_players.add(event.user_id)

        tokens = self.text.split()
        n_tokens = len(tokens)
        modified_tokens = []
        buzzed_players = set()
        for idx, tok in enumerate(tokens):
            for event in filtered_events:
                if event.user_id in buzzed_players or len(buzzed_players) >= max_buzzes:
                    continue

                if idx / n_tokens > event.buzzing_position:
                    buzzed_players.add(event.user_id)
                    if event.result == "wrong":
                        modified_tokens.append(
                            rf'<span class="badge badge-pill badge-danger">{len(buzzed_players)}</span>'
                        )
                    elif event.result == "correct":
                        modified_tokens.append(
                            rf'<span class="badge badge-pill badge-success">{len(buzzed_players)}</span>'
                        )
            modified_tokens.append(tok)
        return " ".join(modified_tokens)


class PlayEvent(Base):
    __tablename__ = "play_event"
    play_id = Column(Integer, primary_key=True)
    qanta_id = Column(Integer, ForeignKey("questions.qanta_id"), index=True)
    user_id = Column(String)
    buzzing_position = Column(Float)
    guess = Column(String)
    result = Column(String)
    date = Column(DateTime, index=True)
    question = relationship("Question", back_populates="plays")

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "buzzing_position": self.buzzing_position,
            "buzzing_position_str": to_precision(self.buzzing_position, 3),
            "guess": self.guess,
            "result": self.result,
            "date": self.date,
        }


class CuriosityDbDialog(Base):
    """
    The full dialog data is stored in `data`.
    Other fields are primarily for convenience for use
    in DB queries.
    """

    __tablename__ = "curiosity_dialog"
    dialog_id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    assistant_id = Column(Integer)
    topic = Column(String)
    aspect_1 = Column(String)
    aspect_2 = Column(String)
    data = Column(String)

    @property
    def url(self):
        return f"https://datasets.pedro.ai/curiosity/dialog/{self.dialog_id}"


def build_db():
    # pylint: disable=bare-except
    log.info("Dropping and Creating DB")
    try:
        Base.metadata.drop_all(bind=engine)
    except:
        pass
    Base.metadata.create_all(bind=engine)
    build_qanta()
    build_curiosity()


def load_curiosity() -> List[CuriosityDialog]:
    dialogs: List[CuriosityDialog] = []
    for fold in ["train", "val", "test", "test_zero"]:
        for d in read_json(f"data/curiosity/curiosity_dialogs.{fold}.json")["dialogs"]:
            dialogs.append((fold, CuriosityDialog(**d)))
    return dialogs


def build_curiosity():
    log.info("Dropping Prior viersion")
    try:
        Base.metadata.tables["curiosity_dialog"].drop(bind=engine)
    except OperationalError:
        pass
    Base.metadata.tables["curiosity_dialog"].create(bind=engine)
    log.info("Loading curiosity dialogs")
    dialogs = load_curiosity()

    with get_db_context() as db:
        log.info("Writing dialogs")
        for _, d in tqdm(dialogs):
            db.add(
                CuriosityDbDialog(
                    dialog_id=d.dialog_id,
                    user_id=d.user_id,
                    assistant_id=d.assistant_id,
                    topic=d.focus_entity,
                    aspect_1=d.first_aspect,
                    aspect_2=d.second_aspect,
                    data=d.json(),
                )
            )
        log.info("Committing dialogs")
        db.commit()


def build_qanta():
    log.info("Loading data")
    with open("data/qanta.mapped.2018.04.18.json") as f:
        questions = json.load(f)["questions"]

    df = pd.read_hdf("data/protobowl-042818.log.h5")
    proto_id_to_qanta = {}

    with get_db_context() as db:
        log.info("Writing questions")
        for q in tqdm(questions):
            if q["proto_id"] is not None:
                proto_id_to_qanta[q["proto_id"]] = q["qanta_id"]
            db.add(
                Question(
                    qanta_id=q["qanta_id"],
                    text=q["text"],
                    first_sentence=q["first_sentence"],
                    tokenizations=json.dumps(q["tokenizations"]),
                    answer=q["answer"],
                    page=q["page"],
                    fold=q["fold"],
                    gameplay=q["gameplay"],
                    category=q["category"],
                    subcategory=q["subcategory"],
                    tournament=q["tournament"],
                    difficulty=q["difficulty"],
                    year=q["year"],
                    proto_id=q["proto_id"],
                    qdb_id=q["qdb_id"],
                    dataset=q["dataset"],
                )
            )
        db.commit()

        log.info("Writing play events")
        n = 0
        for event in tqdm(df.itertuples()):
            if event.qid not in proto_id_to_qanta:
                continue

            if event.result is True:
                result = "correct"
            elif event.result is False:
                result = "wrong"
            elif event.result == "prompt":
                result = "prompt"
            else:
                raise ValueError(f"Unexpected result: {event.result}")

            db.add(
                PlayEvent(
                    qanta_id=proto_id_to_qanta[event.qid],
                    buzzing_position=event.buzzing_position,
                    user_id=event.uid,
                    date=event.date,
                    guess=event.guess,
                    result=result,
                )
            )
            n += 1
        log.info("Found %s matching records", n)
        db.commit()
