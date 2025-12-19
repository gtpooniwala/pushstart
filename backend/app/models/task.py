from typing import Optional, Dict, Any, List
from sqlmodel import SQLModel, Field, Column, JSON
from datetime import datetime

class Task(SQLModel, table=True):
    id: str = Field(primary_key=True)
    content: str
    description: Optional[str] = None
    project_id: Optional[str] = None
    section_id: Optional[str] = None
    parent_id: Optional[str] = None
    priority: int = 1
    due_string: Optional[str] = None
    due_date: Optional[str] = None
    is_completed: bool = False
    labels: Optional[List[str]] = Field(default=None, sa_column=Column(JSON))
    order: Optional[int] = 0
    url: Optional[str] = None
    created_at: Optional[datetime] = None
    
    # Store raw JSON for any extra fields we might miss or want to pass through
    raw_data: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))

from typing import List
