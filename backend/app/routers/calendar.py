from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.db import engine
from app.services.calendar_service import CalendarService

router = APIRouter(
    prefix="/calendar",
    tags=["calendar"],
    responses={404: {"description": "Not found"}},
)

async def get_service():
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield CalendarService(session)

@router.get("/events")
async def list_events(days: int = 7, service: CalendarService = Depends(get_service)):
    """List upcoming calendar events."""
    try:
        return await service.list_events(days=days)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
