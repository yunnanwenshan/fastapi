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


class MembershipStatistics(BaseModel):
    total_members: int
    active_members: int
    inactive_members: int
    average_points: float
    top_level: str
    newest_members_count: int
    expiring_soon_count: int
    created_at: datetime


class LevelDistribution(BaseModel):
    level: str
    count: int
    percentage: float


class MembershipTrend(BaseModel):
    date: datetime
    new_members: int
    churned_members: int
    net_growth: int
    total_members: int


class PointsDistribution(BaseModel):
    range_start: int
    range_end: int
    count: int
    percentage: float


class MembershipTimeFrame(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    level: Optional[str] = None


class MembershipStatsResponse(BaseModel):
    overall: MembershipStatistics
    level_distribution: List[LevelDistribution]
    trends: List[MembershipTrend]
    points_distribution: List[PointsDistribution]