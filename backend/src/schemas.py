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
