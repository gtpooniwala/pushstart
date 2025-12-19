# Phase 2 – Agent Layer for Task Management (LangGraph + MCP)

## Goal

Introduce an LLM-driven **agent layer** that manipulates tasks via chat, while continuing to use **MCP as the only integration mechanism** for Todoist.

The agent can:

- Add tasks via chat  
- Edit tasks via chat  
- Delete tasks via chat  

Still **no calendar integration**, **no scheduling**, and **no guided execution**.

---

## Architecture Overview

- **Frontend:**  
  - Right Panel unchanged  
  - Center Chat panel becomes active
- **Backend:**  
  - FastAPI (REST for frontend)  
  - LangGraph (agent runtime)  
  - MCP Client module (canonical integration layer)
- **Integrations:**  
  - `mcp/todoist_server/` remains the only Todoist API code

**Data Flows:**

Manual:
Frontend → REST → Backend → MCP Client → Todoist MCP Server

makefile
Copy code

Agentic:
Frontend → REST (/chat) → Backend Agent (LangGraph)
→ MCP Client → Todoist MCP Server

yaml
Copy code

---

## Scope

### Backend

#### New Components

##### Chat Endpoint
- `POST /chat`
  - Receives user message
  - Passes message into LangGraph
  - Returns agent response text
- Backend stores chat history (SQLite or Postgres)

##### LangGraph Agent (acts as MCP Client)
Responsibilities:
- Parse intent from chat:
  - “Add a task…”
  - “Rename the last task…”
  - “Delete the grocery task…”
- Execute Todoist actions via the **MCP client**
- Produce natural-language confirmations

Agent explicitly **does not**:
- Use calendar integration
- Suggest times or workflows
- Classify tasks beyond what is needed to fulfill CRUD
- Affect UI state except through CRUD actions

#### MCP Integration
- Same Todoist MCP server as Phase 1
- Backend’s agent nodes call MCP tools directly through:
  - `mcp_client/todoist_client.py`

No new REST integration paths; MCP remains canonical.

---

### Frontend

#### Center Panel – Chat (Active)
- Displays conversation with the agent
- Supports:
  - User messages
  - Agent messages
- No scheduling or advanced features

#### Right Panel – Task List
- Same as Phase 1
- Reflects changes made by the agent via MCP

---

## Out of Scope (Phase 2)

- Calendar access or scheduling
- Approvals tab
- Guided mode
- Multi-step workflows
- Notifications
- Multi-user

All of these move to Phase 3.

---

## User Stories

1. “Add a task to submit expense receipts”  
   → Agent calls MCP → Task appears in UI.

2. “Rename that task to ‘Submit November expenses’”  
   → Task updated via MCP → UI refreshes.

3. “Delete the grocery task”  
   → Agent deletes task via MCP → UI updates.

4. Chat works normally without proposing calendar times.

---

## Acceptance Criteria

- Agent reliably performs create/update/delete via MCP.
- Right Panel reflects agent changes immediately.
- No calendar MCP server is used yet.
- No scheduling or guided logic.
- Chat history persists.
