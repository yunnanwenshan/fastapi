from pydantic import BaseModel
from typing import List, Optional


class Answer(BaseModel):
    question_id: int
    alternative_id: int


class UserAnswer(BaseModel):
    user_id: int
    answers: List[Answer]


class User(BaseModel):
    id: Optional[int] = None
    name: str
    mail: str
    phone: str