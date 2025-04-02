from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Union
from datetime import datetime
from enum import Enum


class Answer(BaseModel):
    question_id: int
    alternative_id: int


class UserAnswer(BaseModel):
    user_id: int
    answers: List[Answer]


# User related models
class User(BaseModel):
    id: int
    name: str
    mail: str
    phone: str
    password: str
    registered_date: datetime
    last_login: Optional[datetime] = None
    member_ids: List[int] = []


class UserLogin(BaseModel):
    email: str
    password: str


class UserRegister(BaseModel):
    name: str
    email: str = Field(..., alias="mail")
    phone: str
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    mail: str
    phone: str
    registered_date: datetime
    last_login: Optional[datetime] = None


class UserDetailResponse(UserResponse):
    member_ids: List[int] = []


# Member related models
class MemberType(str, Enum):
    PERSONAL = "personal"
    CORPORATE = "corporate"


class Member(BaseModel):
    member_id: int
    user_id: int
    member_type: MemberType
    created_date: datetime


class CorporateMember(Member):
    company_name: str
    business_id: str
    industry: str
    employees_count: Optional[int] = None
    website: Optional[str] = None


class PersonalMember(Member):
    first_name: str
    last_name: str
    occupation: str
    birth_date: Optional[datetime] = None


class CorporateMemberCreate(BaseModel):
    company_name: str
    business_id: str
    industry: str
    employees_count: Optional[int] = None
    website: Optional[str] = None


class PersonalMemberCreate(BaseModel):
    first_name: str
    last_name: str
    occupation: str
    birth_date: Optional[datetime] = None


class MemberCreate(BaseModel):
    user_id: int
    member_type: MemberType
    corporate_data: Optional[CorporateMemberCreate] = None
    personal_data: Optional[PersonalMemberCreate] = None


class MemberResponse(BaseModel):
    member_id: int
    user_id: int
    member_type: MemberType
    created_date: datetime
    corporate_data: Optional[CorporateMemberCreate] = None
    personal_data: Optional[PersonalMemberCreate] = None