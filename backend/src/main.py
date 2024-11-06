"""
Module to implement the backend of the Todo List application.

This module implements the backend using:
- FastAPI to create the REST API
- Redis to create cache for the tasks
- SQLAlchemy to interact with the PostgreSQL database
"""

import os
from typing import List
from src import models, schemas
from src.database import engine, SessionLocal
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import redis

load_dotenv(override=True)

redis_client = redis.Redis(
    host=os.getenv("REDIS_SERVER"),
    port=os.getenv("REDIS_PORT"),
    db=0,
)

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    """Generator to get the database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/tasks/", response_model=schemas.TaskRetrieve)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    """Create a new task"""
    db_task = models.Task(title=task.title, description=task.description, completed=task.completed)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    redis_client.set(f"task:{db_task.id}", schemas.TaskRetrieve.from_orm(db_task).json())
    return db_task

@app.get("/tasks/{task_id}", response_model=schemas.TaskRetrieve)
def get_task(task_id: int, db: Session = Depends(get_db)):
    """Get a task by its ID"""
    if (cached_task := redis_client.get(f"task:{task_id}")) is not None:
        return schemas.TaskRetrieve.parse_raw(cached_task)
    if (db_task := db.query(models.Task).filter(models.Task.id == task_id).first()) is None:
        raise HTTPException(status_code=404, detail="Task not found")
    redis_client.set(f"task:{db_task.id}", schemas.TaskRetrieve.from_orm(db_task).json())
    return db_task

@app.put("/tasks/{task_id}", response_model=schemas.TaskRetrieve)
def update_task(task_id: int, task: schemas.TaskUpdate, db: Session = Depends(get_db)):
    """Update a task's status"""
    if (db_task := db.query(models.Task).filter(models.Task.id == task_id).first()) is None:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.title is not None:
        setattr(db_task, "title", task.title)
    if task.description is not None:
        setattr(db_task, "description", task.description)
    if task.completed is not None:
        setattr(db_task, "completed", task.completed)
    db.commit()
    db.refresh(db_task)
    redis_client.set(f"task:{db_task.id}", schemas.TaskRetrieve.from_orm(db_task).json())
    return db_task

@app.delete("/tasks/{task_id}", response_model=schemas.TaskRetrieve)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    """Delete a task"""
    if (db_task := db.query(models.Task).filter(models.Task.id == task_id).first()) is None:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(db_task)
    db.commit()
    redis_client.delete(f"task:{task_id}")
    return db_task

@app.get("/tasks/", response_model=List[schemas.TaskRetrieve])
def list_tasks(db: Session = Depends(get_db), limit: int = 100):
    """List all tasks"""
    if (tasks := db.query(models.Task).limit(limit).all()) == []:
        raise HTTPException(status_code=404, detail="No tasks found")
    return tasks
