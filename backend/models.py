from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Enum, Index
from sqlalchemy.sql import func
from .database import Base
import enum

class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class TaskPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING, nullable=False)
    priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM, nullable=False)
    due_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, onupdate=func.now())
    completed_at = Column(DateTime, nullable=True)
    
    # Assignment
    assigned_to = Column(String(100), nullable=True)
    assigned_email = Column(String(200), nullable=True)
    
    # Notifications
    notification_sent = Column(Boolean, default=False)
    last_notification_at = Column(DateTime, nullable=True)
    
    # Metadata
    tags = Column(String(500), nullable=True)  # Comma-separated tags
    estimated_hours = Column(Integer, default=0)
    actual_hours = Column(Integer, default=0)
    
    # Indexes for better performance
    __table_args__ = (
        Index('idx_due_date_status', 'due_date', 'status'),
        Index('idx_assigned_email', 'assigned_email'),
        Index('idx_priority_status', 'priority', 'status'),
    )
    
    def __repr__(self):
        return f"<Task(id={self.id}, title='{self.title}', status='{self.status}')>"

class TaskComment(Base):
    __tablename__ = "task_comments"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, nullable=False)
    comment = Column(Text, nullable=False)
    created_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    
    __table_args__ = (
        Index('idx_task_comments', 'task_id', 'created_at'),
    )