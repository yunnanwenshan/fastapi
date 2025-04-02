from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import re


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


class LogOperationType(str, Enum):
    login = "login"
    logout = "logout"
    create = "create"
    update = "update"
    delete = "delete"
    view = "view"


class UserLog(BaseModel):
    id: str
    user_id: str
    operation_type: LogOperationType
    description: str
    created_at: datetime
    ip_address: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class CreateLogModel(BaseModel):
    user_id: str
    operation_type: LogOperationType
    description: str
    ip_address: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class LogFilterModel(BaseModel):
    user_id: Optional[str] = None
    operation_type: Optional[LogOperationType] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class UserLogResponse(BaseModel):
    id: str
    user_id: str
    operation_type: LogOperationType
    description: str
    created_at: datetime
    ip_address: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class EmailVerification(BaseModel):
    email: str
    code: str
    created_at: datetime
    expires_at: datetime
    verified: bool = False


class UserRegistration(BaseModel):
    name: str
    mail: str
    phone: str
    password: str
    confirm_password: str


class RegistrationResponse(BaseModel):
    message: str
    user_id: Optional[str] = None
    verification_required: bool = True