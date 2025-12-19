# Phase 2 – Agent Layer for Task Management (LangGraph + MCP)

## Goal

Introduce a lightweight LLM-driven **agent layer** that manipulates tasks via chat, still using **MCP as the only integration layer** for Todoist.

The agent can:

- Add tasks  
- Edit tasks  
- Delete tasks  

No calendar logic yet.

---

## Architecture Overview

- **Frontend:** Chat panel becomes active; Right Panel unchanged
- **Backend:** FastAPI + LangGraph agent
- **Integrations:**  
  - Todoist MCP server (same as Phase 1)

### Data Flows

'''
Manual:
Frontend → REST → Backend → MCP Client Module → Todoist MCP Server

Agentic:
Chat → /chat → Backend Agent → MCP Client Module → Todoist MCP Server
'''

### Architectural Principle

Both manual flows and agent flows run **inside the same backend process**,  
and both call the **same MCP client Python module**.

---

## Scope

### Backend

#### New REST Endpoint

- `POST /chat`
  - Accepts a message
  - Routes to LangGraph agent
  - Returns LLM-generated text
  - Updates chat history

#### LangGraph Agent

The backend agent:

- Interprets user intent (“Add a task…”, “Rename that…”)
- Performs task CRUD by calling MCP tools through the shared MCP client module
- Returns confirmations to the frontend

**Agent does NOT:**

- Propose admin blocks
- Use the calendar
- Classify tasks (beyond minimal IDs)
- Trigger guided execution

#### MCP Integration

- Same Todoist MCP server as Phase 1.
- A shared Python module (`backend/mcp_client/todoist_client.py`) provides:
  - `create_task(title)`
  - `update_task(id, fields)`
  - `delete_task(id)`
  - `list_tasks()`

The **backend process is the MCP client**.  
Agent nodes simply call these helper methods.

---

### Frontend

#### Chat Panel

- Sends/receives messages via `/chat`
- Displays LLM responses

#### Right Panel – Task List

- Automatically refreshes when tasks change

---

## Out of Scope (Phase 2)

- Any calendar access
- Any scheduling proposals
- Approvals tab
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
