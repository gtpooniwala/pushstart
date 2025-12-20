from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Thread(SQLModel, table=True):
    id: str = Field(primary_key=True)
    title: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
