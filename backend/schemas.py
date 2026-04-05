from pydantic import BaseModel, Field, EmailStr, ConfigDict
from datetime import datetime
from typing import Optional, List
from .models import TaskStatus, TaskPriority

# Task Schemas
class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: datetime
    assigned_to: Optional[str] = None
    assigned_email: Optional[EmailStr] = None
    tags: Optional[str] = None
    estimated_hours: int = 0
    actual_hours: int = 0

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None
    assigned_to: Optional[str] = None
    assigned_email: Optional[EmailStr] = None
    tags: Optional[str] = None
    estimated_hours: Optional[int] = None
    actual_hours: Optional[int] = None

class TaskResponse(TaskBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    completed_at: Optional[datetime]
    notification_sent: bool
    last_notification_at: Optional[datetime]
    
    model_config = ConfigDict(from_attributes=True)

# Comment Schemas
class CommentBase(BaseModel):
    comment: str = Field(..., min_length=1)
    created_by: Optional[str] = None

class CommentCreate(CommentBase):
    task_id: int

class CommentResponse(CommentBase):
    id: int
    task_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# Statistics Schemas
class TaskStatistics(BaseModel):
    total: int
    completed: int
    pending: int
    in_progress: int
    overdue: int
    completion_rate: float
    by_priority: dict
    by_status: dict

class NotificationStatus(BaseModel):
    enabled: bool
    last_check: Optional[datetime]
    next_check: Optional[datetime]