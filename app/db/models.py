from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class Answer(BaseModel):
    question_id: int
    alternative_id: int


class UserAnswer(BaseModel):
    user_id: int
    answers: List[Answer]


class User(BaseModel):
    id: str
    name: str
    mail: str
    phone: str
    password_hash: str
    created_at: datetime
    updated_at: datetime


class CreateUserModel(BaseModel):
    name: str
    mail: str
    phone: str
    password: str
    

class UpdateUserModel(BaseModel):
    name: Optional[str] = None
    mail: Optional[str] = None
    phone: Optional[str] = None
    password: Optional[str] = None


class UserResponse(BaseModel):
    id: str
    name: str
    mail: str
    phone: str
    created_at: datetime
    updated_at: datetime


class Membership(BaseModel):
    id: str
    user_id: str
    level: str
    points: int
    valid_from: datetime
    valid_until: datetime
    is_active: bool
    created_at: datetime
    updated_at: datetime


class CreateMembershipModel(BaseModel):
    user_id: str
    level: str
    points: int
    valid_from: datetime
    valid_until: datetime
    is_active: bool = True


class UpdateMembershipModel(BaseModel):
    user_id: Optional[str] = None
    level: Optional[str] = None
    points: Optional[int] = None
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    is_active: Optional[bool] = None


class MembershipResponse(BaseModel):
    id: str
    user_id: str
    level: str
    points: int
    valid_from: datetime
    valid_until: datetime
    is_active: bool
    created_at: datetime
    updated_at: datetime