# pylint: disable=no-name-in-module
from typing import List, Optional
from pydantic import BaseModel


class CuriosityFact(BaseModel):
    fid: int
    used: bool
    source: str


class CuriosityMessage(BaseModel):
    message: str
    liked: bool
    sender: str
    facts: List[CuriosityFact]
    message_id: str
    dialog_acts: List[str]


class CuriosityDialog(BaseModel):
    messages: List[CuriosityMessage]
    known_entities: List[str]
    focus_entity: str
    dialog_id: int
    inferred_steps: bool
    created_time: int
    aspects: List[str]
    first_aspect: Optional[str]
    second_aspect: Optional[str]
    shuffle_facts: bool
    related_entities: List[str]
    tag: str
    user_id: str
    assistant_id: str
    user_dialog_rating: int
    user_other_agent_rating: int
    assistant_dialog_rating: int
    assistant_other_agent_rating: int
    reported: bool
