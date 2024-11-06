"""
Define the database model for the tasks to interact with the database
"""

from sqlalchemy import Column, Integer, String, Boolean
from .database import Base

class Task(Base):
    """Task model"""
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, nullable=True)
    completed = Column(Boolean, default=False)
