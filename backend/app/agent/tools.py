from langchain_core.tools import tool
from typing import Optional
from app.core.db import engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker
from app.services.task_service import TaskService
from app.services.calendar_service import CalendarService
from app.mcp_client.calendar_client import calendar_client

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
        return await service.list_tasks()

@tool
async def list_calendar_events(days: int = 7):
    """List upcoming calendar events."""
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        service = CalendarService(session)
        return await service.list_events(days)

@tool
async def create_calendar_event(summary: str, start_time: str, end_time: str, description: str = ""):
    """Create a new calendar event. Times must be ISO format strings."""
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        service = CalendarService(session)
        return await service.create_event(summary, start_time, end_time, description)

@tool
async def find_free_blocks(duration_minutes: int = 60, days: int = 3):
    """Find free time blocks in the calendar."""
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        service = CalendarService(session)
        return await service.find_free_blocks(duration_minutes, days)

SAFE_TOOLS = [list_tasks, list_calendar_events, find_free_blocks]
SENSITIVE_TOOLS = [create_task, update_task, delete_task, complete_task, create_calendar_event]
ALL_TOOLS = SAFE_TOOLS + SENSITIVE_TOOLS

