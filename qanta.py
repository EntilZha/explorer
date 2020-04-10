import json
from contextlib import contextmanager
import random

from fastapi import APIRouter
from sqlalchemy import Column, Integer, String, Boolean, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


Base = declarative_base()
engine = create_engine('sqlite:///data/qanta.2018.04.18.sqlite3')
Session = sessionmaker(bind=engine)

@contextmanager
def create_session() -> Session:
    session = Session()
    yield session
    session.close()


class Question(Base):
    __tablename__ = 'questions'
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

    def to_dict(self):
        return {
            'qanta_id': self.qanta_id,
            'text': self.text,
            'tokenizations': json.loads(self.tokenizations),
            'answer': self.answer,
            'page': self.page,
            'fold': self.fold,
            'gameplay': self.gameplay,
            'category': self.category,
            'subcategory': self.subcategory,
            'tournament': self.tournament,
            'difficulty': self.difficulty,
            'year': self.year,
            'proto_id': self.proto_id,
            'qdb_id': self.proto_id,
            'dataset': self.dataset
        }


with create_session() as session:
    all_qanta_ids = [r[0] for r in session.query(Question.qanta_id).all()]


router = APIRouter()


@router.get('/api/qanta/v1/random')
def get_random_question():
    with create_session() as session:
        qanta_id = random.choice(all_qanta_ids)
        question = session.query(Question).filter_by(qanta_id=qanta_id).first()
    return question.to_dict()


@router.get("/api/qanta/v1/{qanta_id}")
def get_question(qanta_id: int):
    with create_session() as session:
        question = session.query(Question).filter_by(qanta_id=qanta_id).first()
    return question.to_dict()