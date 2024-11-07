"""
Module to implement the backend of the Todo List application.

This module implements the backend using:
- FastAPI to create the REST API
- Redis to implement a cache
- SQLAlchemy to interact with the PostgreSQL database
- Pydantic to validate the data
- JWT to authenticate the users
- Bleach to sanitize the input data
"""

import os
from typing import List, Annotated
from datetime import datetime, timedelta, timezone
from src import models, schemas
from src.database import engine, SessionLocal
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
import jwt
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from bleach import clean
import redis

load_dotenv(override=True)

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRATION_MINUTES"))

redis_client = redis.Redis(
    host=os.getenv("REDIS_SERVER"),
    port=os.getenv("REDIS_PORT"),
    db=0,
)

models.Base.metadata.create_all(bind=engine)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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

def verify_password(plain_password: str, hashed_password: str):
    """Verify the password by its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str):
    """Hash the password"""
    return pwd_context.hash(password)

def get_user(username: str, db: Session):
    """Attempt to get a user from the database"""
    user = db.query(models.User).filter(models.User.username == username).first()
    return schemas.UserInDB(**user.__dict__) if user else None

def create_user(user: schemas.UserCreate, db: Session):
    """Create a new user"""
    existing_user = db.query(models.User).filter(models.User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    db_user = models.User(
        username=user.username,
        hashed_password=get_password_hash(user.password),
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(username: str, password: str, db: Session):
    """Authenticate the user"""
    user = get_user(username, db)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """Create an access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)],
        db: Session = Depends(get_db)
) -> schemas.User:
    """Get the current user from the token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except InvalidTokenError as exc:
        raise credentials_exception from exc
    user = get_user(username=token_data.username, db=db)
    if user is None:
        raise credentials_exception
    return user

@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
) -> schemas.Token:
    """Login to get an access token"""
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return schemas.Token(access_token=access_token, token_type="bearer")

@app.post("/register", response_model=schemas.User)
async def signup_for_access_token(
    user: schemas.UserCreate,
    db: Session = Depends(get_db),
) -> schemas.UserInDB:
    """Sign up to get an access token"""
    user = create_user(user=user, db=db)
    return user

@app.get("/users/me/", response_model=schemas.User)
async def read_users_me(
    current_user: Annotated[schemas.User, Depends(get_current_user)],
):
    """Get the current user"""
    return current_user

@app.post("/tasks/", response_model=schemas.TaskRetrieve)
def create_task(
    current_user: Annotated[schemas.User, Depends(get_current_user)],
    task: schemas.TaskCreate,
    db: Session = Depends(get_db)
):
    """Create a new task"""
    db_task = models.Task(
        title=clean(task.title),
        description=clean(task.description),
        completed=task.completed
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    redis_client.set(
        f"task:{db_task.id}",
        schemas.TaskRetrieve.model_validate(db_task).model_dump_json()
    )
    return db_task

@app.get("/tasks/{task_id}", response_model=schemas.TaskRetrieve)
def get_task(
    current_user: Annotated[schemas.User, Depends(get_current_user)],
    task_id: int,
    db: Session = Depends(get_db)
):
    """Get a task by its ID"""
    cached_task = redis_client.get(f"task:{task_id}")
    if cached_task is not None:
        return schemas.TaskRetrieve.model_validate_json(cached_task)
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    redis_client.set(
        f"task:{db_task.id}",
        schemas.TaskRetrieve.model_validate(db_task).model_dump_json()
    )
    return db_task

@app.put("/tasks/{task_id}", response_model=schemas.TaskRetrieve)
def update_task(
    current_user: Annotated[schemas.User, Depends(get_current_user)],
    task_id: int,
    task: schemas.TaskUpdate,
    db: Session = Depends(get_db)
):
    """Update a task's status"""
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.title is not None:
        setattr(db_task, "title", clean(task.title))
    if task.description is not None:
        setattr(db_task, "description", clean(task.description))
    if task.completed is not None:
        setattr(db_task, "completed", task.completed)
    db.commit()
    db.refresh(db_task)
    redis_client.set(
        f"task:{db_task.id}",
        schemas.TaskRetrieve.model_validate(db_task).model_dump_json()
    )
    return db_task

@app.delete("/tasks/{task_id}", response_model=schemas.TaskRetrieve)
def delete_task(
    current_user: Annotated[schemas.User, Depends(get_current_user)],
    task_id: int,
    db: Session = Depends(get_db)
):
    """Delete a task"""
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(db_task)
    db.commit()
    redis_client.delete(f"task:{task_id}")
    return db_task

@app.get("/tasks/", response_model=List[schemas.TaskRetrieve])
def list_tasks(
    current_user: Annotated[schemas.User, Depends(get_current_user)],
    db: Session = Depends(get_db),
    limit: int = 100
):
    """List all tasks"""
    tasks = db.query(models.Task).limit(limit).all()
    if tasks == []:
        raise HTTPException(status_code=404, detail="No tasks found")
    return tasks
