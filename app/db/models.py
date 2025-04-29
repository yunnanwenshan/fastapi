from pydantic import BaseModel, Field, validator, EmailStr
from typing import List, Optional
import re


class Answer(BaseModel):
    question_id: int
    alternative_id: int


class UserAnswer(BaseModel):
    user_id: int
    answers: List[Answer]


class UserCreate(BaseModel):
    name: str = Field(..., description="User's full name")
    mail: EmailStr = Field(..., description="User's email address")
    phone: str = Field(..., description="User's phone number")
    
    @validator('name')
    def name_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v
    
    @validator('phone')
    def validate_phone_number(cls, v):
        if not re.match(r'^\d{8,15}$', v):
            raise ValueError('Phone number must be between 8 and 15 digits')
        return v