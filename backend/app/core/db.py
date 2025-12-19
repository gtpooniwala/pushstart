from sqlmodel import SQLModel, create_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
import os
import asyncio
import logging
from app.models.task import Task
from app.models.event import Event

# Docker default
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://pushstart:pushstart_password@localhost:5432/pushstart_db")

engine = create_async_engine(DATABASE_URL, echo=False, future=True)
logger = logging.getLogger(__name__)

async def init_db():
    retries = 10
    for i in range(retries):
        try:
            async with engine.begin() as conn:
                # await conn.run_sync(SQLModel.metadata.drop_all) # For dev only
                await conn.run_sync(SQLModel.metadata.create_all)
            logger.info("Database initialized successfully.")
            return
        except Exception as e:
            if i == retries - 1:
                logger.error(f"Failed to initialize database after {retries} attempts: {e}")
                raise e
            logger.warning(f"Database connection failed, retrying in 2s... (Attempt {i+1}/{retries})")
            await asyncio.sleep(2)

async def get_session() -> AsyncSession:
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session
