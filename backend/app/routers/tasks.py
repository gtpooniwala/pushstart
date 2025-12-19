from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Any
from app.mcp_client.todoist_client import todoist_client

router = APIRouter()

class TaskCreate(BaseModel):
    content: str
    description: Optional[str] = None
    due_string: Optional[str] = None
    priority: Optional[int] = None

class TaskUpdate(BaseModel):
    content: Optional[str] = None
    description: Optional[str] = None
    due_string: Optional[str] = None
    priority: Optional[int] = None

@router.get("/")
async def get_tasks():
    """Fetch all tasks via MCP."""
    try:
        return await todoist_client.list_tasks()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
async def create_task(task: TaskCreate):
    """Create a task via MCP."""
    try:
        return await todoist_client.create_task(
            content=task.content,
            description=task.description,
            due_string=task.due_string,
            priority=task.priority
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{task_id}")
async def update_task(task_id: str, task: TaskUpdate):
    """Update a task via MCP."""
    try:
        return await todoist_client.update_task(
            task_id=task_id,
            content=task.content,
            description=task.description,
            due_string=task.due_string,
            priority=task.priority
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{task_id}")
async def delete_task(task_id: str):
    """Delete a task via MCP."""
    try:
        return await todoist_client.delete_task(task_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{task_id}/close")
async def close_task(task_id: str):
    """Close (complete) a task via MCP."""
    try:
        return await todoist_client.close_task(task_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
