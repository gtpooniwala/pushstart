# Phase 1 – Manual Task Hub (Todoist + MCP Only)

## Goal

Build the simplest viable version of Pushstart as a **manual task manager** backed by **Todoist**, using **MCP as the single integration mechanism**.  
No agents, no LLMs, no scheduling, no calendar logic.

This phase establishes:

- The Right Panel Task UI
- REST CRUD endpoints in the backend
- Todoist integration through a **local Todoist MCP server**
- A shared MCP client module used by all backend code

---

## Architecture Overview

- **Frontend:** Next.js  
- **Backend:** FastAPI (Python)
- **Integrations:**  
  - `mcp/todoist_server/` (the only place with Todoist API code)

### Data Flow (Phase 1)

Frontend UI → REST → Backend → MCP Client Module → Todoist MCP Server → Todoist API

### Key Architectural Principle

The **backend process itself is the MCP client**.  
A shared Python module (`backend/mcp_client/todoist_client.py`) wraps MCP JSON-RPC calls for reuse.

---

## Scope

### Backend (FastAPI)

#### Responsibilities

- Define REST endpoints that wrap Todoist CRUD calls through MCP.
- No business logic beyond simple validation.
- No task classification or agent behaviour.

#### Endpoints

- `GET /tasks`  
  Fetch tasks via MCP.
- `POST /tasks`  
  Create a Todoist task via MCP.
- `PUT /tasks/{id}`  
  Update Todoist task fields.
- `DELETE /tasks/{id}` (optional)

#### MCP Integration

- A shared module `mcp_client/todoist_client.py`:
  - Creates the MCP connection
  - Calls MCP tools like `todoist.create_task`, `todoist.list_tasks`
- Backend code imports this module directly.
- MCP server is assumed running (manual or “start on first use”).

### Frontend

#### Right Panel – Task List

- List tasks (via backend)
- Add/edit/complete/delete tasks
- Reflects Todoist state immediately

#### Center Panel – Chat

- Placeholder only (inactive in Phase 1)

---

## Out of Scope

- Any LLM or agent code
- Task classification
- Calendar integration
- Scheduling
- Approvals
- Guided mode
- Multi-user logic

---

## User Stories

1. I can add a task manually and see it in Todoist and the UI.
2. I can edit a task.
3. I can complete or delete a task.
4. Reloading the page reloads tasks via MCP.

---

## Acceptance Criteria

- Backend uses MCP exclusively for Todoist access.
- UI CRUD works reliably.
- No LLM logic exists.
- Todoist is the persistence layer.
