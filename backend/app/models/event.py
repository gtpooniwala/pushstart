from typing import Optional, Dict, Any
from sqlmodel import SQLModel, Field, Column, JSON
from datetime import datetime

class Event(SQLModel, table=True):
    id: str = Field(primary_key=True)
    summary: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    status: Optional[str] = None
    html_link: Optional[str] = None
    
    # Store raw JSON for any extra fields
    raw_data: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
