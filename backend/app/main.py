from dotenv import load_dotenv
import os
from pathlib import Path

# Load .env from root
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import tasks, chat, calendar, guided
from app.core.db import init_db
from app.agent.graph import close_graph

app = FastAPI(title="Pushstart Backend")

@app.on_event("startup")
async def on_startup():
    await init_db()

@app.on_event("shutdown")
async def on_shutdown():
    await close_graph()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(calendar.router)
app.include_router(guided.router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
