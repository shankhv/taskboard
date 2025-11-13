from pydantic import BaseModel
from typing import List, Optional, Generic, TypeVar

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    next_cursor: Optional[str] = None
    prev_cursor: Optional[str] = None

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
