# Phase 1 – Manual Task Hub (Todoist + MCP Only)

## Goal

Build the simplest viable version of Pushstart as a **manual task manager** backed by **Todoist**, using **MCP as the sole integration mechanism**, with no agents, no LLMs, and no calendar logic.

This phase establishes:

- The Right Panel UI (Task List)
- Task CRUD through a backend REST API
- Todoist integration via a **local Todoist MCP server**
- A backend architecture that uses an **MCP client as its only integration layer**
- A clean foundation for later agentic behaviour

---

## Architecture Overview

- **Frontend:** Next.js (TS)  
  - Uses REST endpoints exposed by the backend
- **Backend:** FastAPI (Python)  
  - Uses an internal **mcp_client** module to communicate with MCP servers
- **Integrations:**  
  - `mcp/todoist_server/` (the *only* place with Todoist API logic)
- **No agent framework or LLM usage yet**

**Data Flow (Manual only):**
Frontend → REST → Backend → MCP Client → Todoist MCP Server → Todoist API

markdown
Copy code

---

## Scope

### Backend (FastAPI)

#### Responsibilities
- Expose REST endpoints for manual CRUD operations.
- Use the **MCP client** for all Todoist operations.
- No direct REST/SDK usage of Todoist inside backend.
- No classification, scheduling, or LLM involvement.

#### Endpoints
- `GET /tasks`
  - Fetch tasks via MCP.
- `POST /tasks`
  - Create a Todoist task via MCP.
- `PUT /tasks/{id}`
  - Edit Todoist task via MCP.
- `DELETE /tasks/{id}` (optional)
  - Delete/archive a Todoist task via MCP.

#### MCP Integration
- Backend calls a lightweight **McpTodoistClient** module:
  - `mcp_client/todoist_client.py`
- MCP server:
  - Lives in `mcp/todoist_server/`
  - Backend connects over stdio/pipe or socket.
- Phase 1 startup assumptions:
  - MCP server may be manually started  
  - or backend may implement "start on first request"

### Frontend (Next.js)

#### Right Panel – Task List (Functional)
- Fetch and render Todoist tasks.
- Add tasks through backend → MCP.
- Edit tasks.
- Complete/uncomplete tasks.
- Delete tasks (optional).

#### Center Panel – Chat
- Placeholder UI only.
- No agent or chat behaviour yet.

---

## Out of Scope
- LLM usage
- Chat understanding
- Task classification
- Scheduling or calendar tools
- Approvals tab
- Guided workflows
- Multi-user
- Any direct API access (backend must use MCP only)

---

## User Stories

1. I can manually add a task that shows in Todoist and in the UI.
2. I can edit a task and see updates reflected in Todoist.
3. I can mark a task complete via the UI.
4. Refreshing the UI reloads tasks via MCP.
5. No agent or LLM behaviour occurs.

---

## Acceptance Criteria
- Backend uses MCP only for Todoist access—no direct REST calls.
- UI CRUD operations work reliably.
- No calendar logic exists.
- No agent logic exists.
- Task state persists through Todoist.
