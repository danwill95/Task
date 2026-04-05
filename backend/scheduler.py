from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session
from datetime import datetime
from .database import SessionLocal
from .crud import TaskCRUD
from .notifier import notifier
from .config import settings
import logging

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()

def check_and_send_notifications():
    """Check for tasks due soon and send notifications"""
    db = SessionLocal()
    try:
        tasks_due_soon = TaskCRUD.get_tasks_due_soon(db, settings.notification_hours_before)
        
        for task in tasks_due_soon:
            if task.assigned_email and not task.notification_sent:
                success = notifier.send_task_notification(
                    task.assigned_email,
                    task.title,
                    task.due_date.strftime("%d/%m/%Y %H:%M"),
                    task.id
                )
                if success:
                    TaskCRUD.mark_notification_sent(db, task.id)
                    logger.info(f"Notification sent for task {task.id}")
        
        # Check for overdue tasks and log them
        overdue_tasks = TaskCRUD.get_overdue_tasks(db)
        if overdue_tasks:
            logger.warning(f"Found {len(overdue_tasks)} overdue tasks")
            
    except Exception as e:
        logger.error(f"Error in notification check: {e}")
    finally:
        db.close()

def cleanup_old_tasks():
    """Optional: Clean up old completed tasks"""
    db = SessionLocal()
    try:
        # Implement cleanup logic if needed
        logger.info("Running task cleanup...")
    finally:
        db.close()

def start_scheduler():
    """Start the background scheduler"""
    if not scheduler.running:
        # Check for notifications every hour
        scheduler.add_job(
            check_and_send_notifications,
            trigger=IntervalTrigger(seconds=settings.notification_check_interval),
            id='notification_check',
            replace_existing=True
        )
        
        # Daily cleanup at 2 AM
        scheduler.add_job(
            cleanup_old_tasks,
            trigger=CronTrigger(hour=2, minute=0),
            id='daily_cleanup',
            replace_existing=True
        )
        
        scheduler.start()
        logger.info("Scheduler started successfully")
        
        # Run initial check
        check_and_send_notifications()

def stop_scheduler():
    """Stop the background scheduler"""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler stopped")