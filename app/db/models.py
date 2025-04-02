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

class ProjectStatus(str, Enum):
    not_started = "not_started"
    in_progress = "in_progress"
    completed = "completed"
    on_hold = "on_hold"
    cancelled = "cancelled"

class TaskStatus(str, Enum):
    backlog = "backlog"
    todo = "todo"
    in_progress = "in_progress"
    review = "review"
    done = "done"

class TaskPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"

class ProjectRole(str, Enum):
    owner = "owner"
    admin = "admin"
    member = "member"
    guest = "guest"

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

class Project(BaseModel):
    id: str
    name: str
    description: str
    status: ProjectStatus
    created_by: str
    created_at: datetime
    updated_at: datetime
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    priority: str
    metadata: Optional[Dict[str, Any]] = None

class CreateProjectModel(BaseModel):
    name: str
    description: str
    status: ProjectStatus
    created_by: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    priority: str
    metadata: Optional[Dict[str, Any]] = None

class UpdateProjectModel(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    priority: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class ProjectResponse(Project):
    pass

class Task(BaseModel):
    id: str
    project_id: str
    title: str
    description: str
    status: TaskStatus
    priority: TaskPriority
    assigned_to: Optional[str] = None
    created_by: str
    created_at: datetime
    updated_at: datetime
    due_date: Optional[datetime] = None
    estimated_hours: Optional[float] = None
    actual_hours: Optional[float] = None
    parent_task_id: Optional[str] = None
    dependencies: List[str] = []

class CreateTaskModel(BaseModel):
    project_id: str
    title: str
    description: str
    status: TaskStatus
    priority: TaskPriority
    assigned_to: Optional[str] = None
    created_by: str
    due_date: Optional[datetime] = None
    estimated_hours: Optional[float] = None
    actual_hours: Optional[float] = None
    parent_task_id: Optional[str] = None
    dependencies: List[str] = []

class UpdateTaskModel(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    assigned_to: Optional[str] = None
    due_date: Optional[datetime] = None
    estimated_hours: Optional[float] = None
    actual_hours: Optional[float] = None
    parent_task_id: Optional[str] = None
    dependencies: Optional[List[str]] = None

class TaskResponse(Task):
    pass

class ProjectMember(BaseModel):
    id: str
    project_id: str
    user_id: str
    role: ProjectRole
    joined_at: datetime
    invited_by: Optional[str] = None

class CreateProjectMemberModel(BaseModel):
    project_id: str
    user_id: str
    role: ProjectRole
    invited_by: Optional[str] = None

class UpdateProjectMemberModel(BaseModel):
    role: Optional[ProjectRole] = None
    invited_by: Optional[str] = None

class ProjectMemberResponse(ProjectMember):
    pass

class Comment(BaseModel):
    id: str
    content: str
    created_by: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    project_id: str
    task_id: Optional[str] = None
    parent_id: Optional[str] = None

class CreateCommentModel(BaseModel):
    content: str
    created_by: str
    project_id: str
    task_id: Optional[str] = None
    parent_id: Optional[str] = None

class UpdateCommentModel(BaseModel):
    content: Optional[str] = None

class CommentResponse(Comment):
    pass

class Attachment(BaseModel):
    id: str
    filename: str
    file_path: str
    file_size: int
    mime_type: str
    uploaded_by: str
    uploaded_at: datetime
    project_id: str
    task_id: Optional[str] = None

class CreateAttachmentModel(BaseModel):
    filename: str
    file_path: str
    file_size: int
    mime_type: str
    uploaded_by: str
    project_id: str
    task_id: Optional[str] = None

class UpdateAttachmentModel(BaseModel):
    filename: Optional[str] = None
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    mime_type: Optional[str] = None

class AttachmentResponse(Attachment):
    pass

class ProjectStatistics(BaseModel):
    progress: float
    task_status_distribution: Dict[TaskStatus, int]
    total_tasks: int
    completed_tasks: int
    overdue_tasks: int
    created_at: datetime