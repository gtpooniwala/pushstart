from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Any
from sqlmodel.ext.asyncio.session import AsyncSession
from app.core.db import get_session
from app.services.task_service import TaskService

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
async def get_tasks(session: AsyncSession = Depends(get_session)):
    """Fetch all tasks from local DB."""
    service = TaskService(session)
    return await service.get_all_tasks()

@router.post("/sync")
async def sync_tasks(session: AsyncSession = Depends(get_session)):
    """Trigger full sync from Todoist to local DB."""
    service = TaskService(session)
    return await service.sync_tasks()

@router.post("/")
async def create_task(task: TaskCreate, session: AsyncSession = Depends(get_session)):
    """Create a task via MCP and update local DB."""
    try:
        service = TaskService(session)
        return await service.create_task(
            content=task.content,
            description=task.description,
            due_string=task.due_string,
            priority=task.priority
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{task_id}")
async def update_task(task_id: str, task: TaskUpdate, session: AsyncSession = Depends(get_session)):
    """Update a task via MCP and update local DB."""
    try:
        service = TaskService(session)
        return await service.update_task(
            task_id=task_id,
            content=task.content,
            description=task.description,
            due_string=task.due_string,
            priority=task.priority
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{task_id}")
async def delete_task(task_id: str, session: AsyncSession = Depends(get_session)):
    """Delete a task via MCP and local DB."""
    try:
        service = TaskService(session)
        await service.delete_task(task_id)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{task_id}/close")
async def close_task(task_id: str, session: AsyncSession = Depends(get_session)):
    """Close (complete) a task via MCP and remove from local DB."""
    try:
        service = TaskService(session)
        await service.close_task(task_id)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
