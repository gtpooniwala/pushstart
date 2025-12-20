from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from app.services.task_service import TaskService
from app.core.db import engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker
import uuid

router = APIRouter(prefix="/guided", tags=["guided"])

# In-memory session store
sessions: Dict[str, Dict] = {}

class GuidedSessionStart(BaseModel):
    duration_minutes: int = 30
    labels: List[str] = ["admin"]

class GuidedSessionState(BaseModel):
    session_id: str
    current_task: Optional[Dict[str, Any]]
    remaining_tasks: int
    completed_tasks: int

async def get_task_service():
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield TaskService(session)

@router.post("/start", response_model=GuidedSessionState)
async def start_session(params: GuidedSessionStart, service: TaskService = Depends(get_task_service)):
    # Get tasks
    all_tasks = await service.list_tasks()
    
    # Filter tasks
    # 1. By label
    filtered = [t for t in all_tasks if any(l in t.labels for l in params.labels)]
    
    # 2. If not enough, take top priority
    if not filtered:
        # Sort by priority (descending)
        filtered = sorted(all_tasks, key=lambda t: t.priority, reverse=True)[:5]
    
    session_id = str(uuid.uuid4())
    # Store as dicts using model_dump()
    sessions[session_id] = {
        "tasks": [t.model_dump() for t in filtered], 
        "current_index": 0,
        "completed_count": 0
    }
    
    current_task = sessions[session_id]["tasks"][0] if sessions[session_id]["tasks"] else None
    
    return GuidedSessionState(
        session_id=session_id,
        current_task=current_task,
        remaining_tasks=len(sessions[session_id]["tasks"]),
        completed_tasks=0
    )

@router.post("/{session_id}/next", response_model=GuidedSessionState)
async def next_task(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    session["current_index"] += 1
    
    idx = session["current_index"]
    tasks = session["tasks"]
    
    current_task = tasks[idx] if idx < len(tasks) else None
    
    return GuidedSessionState(
        session_id=session_id,
        current_task=current_task,
        remaining_tasks=max(0, len(tasks) - idx),
        completed_tasks=session["completed_count"]
    )

@router.post("/{session_id}/complete", response_model=GuidedSessionState)
async def complete_current_task(session_id: str, service: TaskService = Depends(get_task_service)):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    idx = session["current_index"]
    tasks = session["tasks"]
    
    if idx < len(tasks):
        task = tasks[idx]
        # Complete in Todoist
        await service.close_task(task["id"])
        session["completed_count"] += 1
    
    # Move to next
    return await next_task(session_id)

@router.post("/{session_id}/skip", response_model=GuidedSessionState)
async def skip_current_task(session_id: str):
    # Just move next without completing
    return await next_task(session_id)
