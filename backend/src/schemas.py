"""
Define the Pydantic schemas for the tasks, used for data validation
"""

from typing import Optional
from pydantic import BaseModel, Field

class TaskCreate(BaseModel):
    """TaskCreate schema"""
    title: str = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=500)
    completed: Optional[bool] = False

class TaskUpdate(BaseModel):
    """TaskUpdate schema"""
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=500)
    completed: Optional[bool] = None

class TaskRetrieve(BaseModel):
    """TaskRetrieve schema"""
    id: int
    title: str
    description: Optional[str]
    completed: bool

    class Config:
        """Pydantic configuration"""
        from_attributes = True

class Token(BaseModel):
    """Token schema"""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """TokenData schema"""
    username: str | None = None

class User(BaseModel):
    """User schema for authentication"""
    username: str

class UserCreate(User):
    """UserCreate schema"""
    password: str

class UserInDB(User):
    """User schema for database"""
    hashed_password: str
