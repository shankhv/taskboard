from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime
from app.entities.task import TaskStatus


class CreateTaskRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=2000)
    due_date: datetime
    category_ids: List[str] = Field(default_factory=list)
    tag_ids: List[str] = Field(default_factory=list)

    @field_validator('due_date')
    @classmethod
    def validate_due_date(cls, v):
        if v < datetime.utcnow():
            raise ValueError('due_date must be in the future')
        return v


class UpdateTaskStatusRequest(BaseModel):
    status: TaskStatus


class TaskResponse(BaseModel):
    id: str
    title: str
    description: str
    due_date: datetime
    status: TaskStatus
    created_at: datetime
    updated_at: datetime
    categories: List[str] = []
    tags: List[str] = []

    class Config:
        from_attributes = True
