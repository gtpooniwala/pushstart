from langchain_core.tools import tool
from typing import Optional
from app.core.db import engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker
from app.services.task_service import TaskService

async def get_service():
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield TaskService(session)

@tool
async def create_task(content: str, description: Optional[str] = None, due_string: Optional[str] = None, priority: Optional[int] = None):
    """Create a new task in Todoist."""
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        service = TaskService(session)
        return await service.create_task(content, description, due_string, priority)

@tool
async def update_task(task_id: str, content: Optional[str] = None, description: Optional[str] = None, due_string: Optional[str] = None, priority: Optional[int] = None):
    """Update an existing task in Todoist."""
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        service = TaskService(session)
        return await service.update_task(task_id, content, description, due_string, priority)

@tool
async def delete_task(task_id: str):
    """Delete a task in Todoist."""
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        service = TaskService(session)
        await service.delete_task(task_id)
        return {"status": "success"}

@tool
async def complete_task(task_id: str):
    """Complete a task in Todoist."""
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        service = TaskService(session)
        await service.close_task(task_id)
        return {"status": "success"}

@tool
async def list_tasks():
    """List all active tasks from local cache."""
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        service = TaskService(session)
        return await service.get_all_tasks()

SAFE_TOOLS = [list_tasks]
SENSITIVE_TOOLS = [create_task, update_task, delete_task, complete_task]
ALL_TOOLS = SAFE_TOOLS + SENSITIVE_TOOLS

