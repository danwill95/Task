from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import logging

from .config import settings
from .database import get_db, init_db
from . import models, schemas, crud
from .scheduler import start_scheduler, stop_scheduler
from .notifier import notifier

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(settings.log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Task Management System with Notifications",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    logger.info("Starting up Task Manager API...")
    init_db()
    start_scheduler()
    logger.info("Task Manager API started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Task Manager API...")
    stop_scheduler()
    logger.info("Task Manager API stopped")

# Health check
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": settings.app_version,
        "notifications_enabled": notifier.enabled
    }

# Task endpoints
@app.post("/tasks", response_model=schemas.TaskResponse, status_code=status.HTTP_201_CREATED, tags=["Tasks"])
async def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    """Create a new task"""
    try:
        return crud.TaskCRUD.create_task(db, task)
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tasks", response_model=List[schemas.TaskResponse], tags=["Tasks"])
async def list_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status: Optional[str] = None,
    priority: Optional[str] = None,
    assigned_to: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all tasks with optional filters"""
    return crud.TaskCRUD.get_tasks(
        db, skip=skip, limit=limit, 
        status=status, priority=priority,
        assigned_to=assigned_to, search=search
    )

@app.get("/tasks/{task_id}", response_model=schemas.TaskResponse, tags=["Tasks"])
async def get_task(task_id: int, db: Session = Depends(get_db)):
    """Get a specific task by ID"""
    task = crud.TaskCRUD.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.put("/tasks/{task_id}", response_model=schemas.TaskResponse, tags=["Tasks"])
async def update_task(task_id: int, task_update: schemas.TaskUpdate, db: Session = Depends(get_db)):
    """Update an existing task"""
    task = crud.TaskCRUD.update_task(db, task_id, task_update)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Tasks"])
async def delete_task(task_id: int, db: Session = Depends(get_db)):
    """Delete a task"""
    success = crud.TaskCRUD.delete_task(db, task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")

@app.get("/tasks/overdue", response_model=List[schemas.TaskResponse], tags=["Tasks"])
async def get_overdue_tasks(db: Session = Depends(get_db)):
    """Get all overdue tasks"""
    return crud.TaskCRUD.get_overdue_tasks(db)

@app.get("/tasks/due-soon", response_model=List[schemas.TaskResponse], tags=["Tasks"])
async def get_tasks_due_soon(
    hours: int = Query(24, ge=1, le=168),
    db: Session = Depends(get_db)
):
    """Get tasks due in the next X hours"""
    return crud.TaskCRUD.get_tasks_due_soon(db, hours)

@app.get("/statistics", response_model=schemas.TaskStatistics, tags=["Statistics"])
async def get_statistics(db: Session = Depends(get_db)):
    """Get task statistics"""
    return crud.TaskCRUD.get_statistics(db)

# Comment endpoints
@app.post("/comments", response_model=schemas.CommentResponse, status_code=status.HTTP_201_CREATED, tags=["Comments"])
async def create_comment(comment: schemas.CommentCreate, db: Session = Depends(get_db)):
    """Add a comment to a task"""
    # Verify task exists
    task = crud.TaskCRUD.get_task(db, comment.task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return crud.CommentCRUD.create_comment(db, comment)

@app.get("/tasks/{task_id}/comments", response_model=List[schemas.CommentResponse], tags=["Comments"])
async def get_task_comments(task_id: int, skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    """Get all comments for a task"""
    return crud.CommentCRUD.get_comments(db, task_id, skip, limit)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug
    )