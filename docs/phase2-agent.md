# Phase 2 – Agent Layer for Task Management (LangGraph + MCP)

## Goal

Introduce a lightweight LLM-driven **agent layer** that manipulates tasks via chat, still using **MCP as the only integration layer** for Todoist.

The agent can:

- Add tasks  
- Edit tasks  
- Delete tasks  
- List tasks (from local cache)

No calendar logic yet.

---

## Status Checklist

- [x] **LangGraph Agent**: Implemented with `MemorySaver` for state persistence.
- [x] **Human-in-the-Loop (HITL)**: Agent pauses for "sensitive" tools (create/update/delete) requiring user approval.
- [x] **Local Database Cache**: PostgreSQL (Docker) + SQLModel implemented.
- [x] **Write-Through Policy**: All writes go to Todoist (MCP) -> Local DB. Reads come from Local DB.
- [x] **Frontend Chat UI**: Chat panel with collapsible tool outputs and "Proposed Action" cards.
- [x] **Sync Mechanism**: Manual sync button and auto-update on writes.
- [x] **Chat History**: Persistence of chat sessions (using `langgraph-checkpoint-postgres`).
- [x] **Sidebar Enhancements**: Workflow selection (History), Agent mode switching (New Chat).

---

## Architecture Overview

- **Frontend:** Chat panel active; Right Panel displays tasks from local DB.
- **Backend:** FastAPI + LangGraph agent + PostgreSQL (Docker).
- **Integrations:**  
  - Todoist MCP server (same as Phase 1)
  - Local PostgreSQL Cache

### Data Flows

'''
Manual:
Frontend → REST (TaskService) → MCP Client → Todoist
                              ↘ Local DB (Cache Update)

Agentic:
Chat → /chat → Backend Agent → TaskService → MCP Client → Todoist
                                           ↘ Local DB (Cache Update)
'''

### Architectural Principle

**"Write-Through Cache"**:
1.  **Reads**: Always read from the local PostgreSQL database for speed and stability.
2.  **Writes**: Always execute on Todoist via MCP first, then immediately update the local database.
3.  **Sync**: A `/sync` endpoint performs a full reconciliation (fetch all -> upsert -> delete stale).

---

## Scope

### Backend

#### New REST Endpoint

- `POST /chat`
  - Accepts a message
  - Routes to LangGraph agent
  - Returns LLM-generated text or "Proposed Action"
  - Handles Approval/Rejection of sensitive tools

#### LangGraph Agent

The backend agent:

- Interprets user intent (“Add a task…”, “Rename that…”)
- Uses `TaskService` tools to perform actions.
- **Safe Tools**: `list_tasks` (runs automatically).
- **Sensitive Tools**: `create_task`, `update_task`, `delete_task` (requires approval).

#### MCP Integration

- A shared Python module (`backend/mcp_client/todoist_client.py`) wraps the MCP server.
- **TaskService** (`backend/app/services/task_service.py`) orchestrates the calls between MCP and Local DB.

---

### Frontend

#### Chat Panel

- Sends/receives messages via `/chat`
- Displays "Proposed Action" cards for sensitive tools.
- Allows User to "Approve" or "Reject" actions.

#### Right Panel – Task List

- Displays tasks from the local database.
- Includes a "Sync" button to force a refresh from Todoist.

---

## Out of Scope (Phase 2)

- Any calendar access
- Any scheduling proposals
- Guided mode

- Multi-user support

---

## User Stories

1. “Add a task to submit expense receipts” → task appears.
2. “Rename that task to ‘Submit November expenses’” → title updates.
3. “Delete the grocery task” → task removed.
4. Chat interactions do not affect calendar or scheduling.

---

## Acceptance Criteria

- Agent reliably handles task CRUD via MCP.
- Right Panel updates automatically.
- No calendar MCP usage.
- Chat and task flows coexist cleanly.
