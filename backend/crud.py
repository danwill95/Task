from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from datetime import datetime, timedelta
from typing import Optional, List
from . import models, schemas

class TaskCRUD:
    @staticmethod
    def get_task(db: Session, task_id: int) -> Optional[models.Task]:
        return db.query(models.Task).filter(models.Task.id == task_id).first()
    
    @staticmethod
    def get_tasks(
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        assigned_to: Optional[str] = None,
        search: Optional[str] = None
    ) -> List[models.Task]:
        query = db.query(models.Task)
        
        if status:
            query = query.filter(models.Task.status == status)
        if priority:
            query = query.filter(models.Task.priority == priority)
        if assigned_to:
            query = query.filter(models.Task.assigned_to == assigned_to)
        if search:
            query = query.filter(
                or_(
                    models.Task.title.contains(search),
                    models.Task.description.contains(search)
                )
            )
        
        return query.order_by(desc(models.Task.created_at)).offset(skip).limit(limit).all()
    
    @staticmethod
    def create_task(db: Session, task: schemas.TaskCreate) -> models.Task:
        db_task = models.Task(**task.model_dump())
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        return db_task
    
    @staticmethod
    def update_task(db: Session, task_id: int, task_update: schemas.TaskUpdate) -> Optional[models.Task]:
        db_task = TaskCRUD.get_task(db, task_id)
        if db_task:
            update_data = task_update.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_task, field, value)
            
            # Update completed_at if status changed to completed
            if 'status' in update_data and update_data['status'] == models.TaskStatus.COMPLETED:
                db_task.completed_at = datetime.now()
            
            db.commit()
            db.refresh(db_task)
        return db_task
    
    @staticmethod
    def delete_task(db: Session, task_id: int) -> bool:
        db_task = TaskCRUD.get_task(db, task_id)
        if db_task:
            db.delete(db_task)
            db.commit()
            return True
        return False
    
    @staticmethod
    def get_overdue_tasks(db: Session) -> List[models.Task]:
        return db.query(models.Task).filter(
            and_(
                models.Task.due_date < datetime.now(),
                models.Task.status != models.TaskStatus.COMPLETED,
                models.Task.status != models.TaskStatus.CANCELLED
            )
        ).order_by(models.Task.due_date).all()
    
    @staticmethod
    def get_tasks_due_soon(db: Session, hours: int = 24) -> List[models.Task]:
        now = datetime.now()
        deadline = now + timedelta(hours=hours)
        return db.query(models.Task).filter(
            and_(
                models.Task.due_date.between(now, deadline),
                models.Task.status != models.TaskStatus.COMPLETED,
                models.Task.notification_sent == False
            )
        ).all()
    
    @staticmethod
    def get_statistics(db: Session) -> schemas.TaskStatistics:
        tasks = db.query(models.Task).all()
        total = len(tasks)
        
        completed = len([t for t in tasks if t.status == models.TaskStatus.COMPLETED])
        pending = len([t for t in tasks if t.status == models.TaskStatus.PENDING])
        in_progress = len([t for t in tasks if t.status == models.TaskStatus.IN_PROGRESS])
        
        now = datetime.now()
        overdue = len([t for t in tasks if t.due_date < now and t.status != models.TaskStatus.COMPLETED])
        
        by_priority = {
            "low": len([t for t in tasks if t.priority == models.TaskPriority.LOW]),
            "medium": len([t for t in tasks if t.priority == models.TaskPriority.MEDIUM]),
            "high": len([t for t in tasks if t.priority == models.TaskPriority.HIGH]),
            "urgent": len([t for t in tasks if t.priority == models.TaskPriority.URGENT])
        }
        
        by_status = {
            "pending": pending,
            "in_progress": in_progress,
            "completed": completed,
            "cancelled": len([t for t in tasks if t.status == models.TaskStatus.CANCELLED])
        }
        
        completion_rate = (completed / total * 100) if total > 0 else 0
        
        return schemas.TaskStatistics(
            total=total,
            completed=completed,
            pending=pending,
            in_progress=in_progress,
            overdue=overdue,
            completion_rate=completion_rate,
            by_priority=by_priority,
            by_status=by_status
        )
    
    @staticmethod
    def mark_notification_sent(db: Session, task_id: int):
        task = TaskCRUD.get_task(db, task_id)
        if task:
            task.notification_sent = True
            task.last_notification_at = datetime.now()
            db.commit()
            return True
        return False

class CommentCRUD:
    @staticmethod
    def get_comments(db: Session, task_id: int, skip: int = 0, limit: int = 50) -> List[models.TaskComment]:
        return db.query(models.TaskComment).filter(
            models.TaskComment.task_id == task_id
        ).order_by(desc(models.TaskComment.created_at)).offset(skip).limit(limit).all()
    
    @staticmethod
    def create_comment(db: Session, comment: schemas.CommentCreate) -> models.TaskComment:
        db_comment = models.TaskComment(**comment.model_dump())
        db.add(db_comment)
        db.commit()
        db.refresh(db_comment)
        return db_comment