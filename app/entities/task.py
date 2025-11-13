from datetime import datetime
from typing import Optional
from enum import Enum

class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    OVERDUE = "overdue"

class Task:
    def __init__(
        self,
        title: str,
        description: str,
        due_date: datetime,
        status: TaskStatus = TaskStatus.PENDING,
        id: Optional[str] = None,
        deleted: bool = False,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id = id
        self.title = title
        self.description = description
        self.due_date = due_date
        self.status = status
        self.deleted = deleted
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def to_dict(self):
        return {
            "_id": self.id,
            "title": self.title,
            "description": self.description,
            "due_date": self.due_date,
            "status": self.status,
            "deleted": self.deleted,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }