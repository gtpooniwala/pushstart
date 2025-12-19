# Phase 3 – Calendar, Scheduling, and Guided Execution (MCP-First)

## Goal

Extend Pushstart into a full productivity assistant by adding:

- Calendar reading via Google Calendar MCP
- Admin block proposals
- HITL approvals for calendar modifications
- Guided execution mode for admin sessions
- Task classification + scheduling logic

Todoist and Calendar remain fully isolated behind MCP servers.

---

## Architecture Overview

- **Frontend:**  
  - Chat  
  - Right Panel  
  - Approvals Tab  
  - Guided Mode UI
- **Backend:**  
  - FastAPI  
  - LangGraph agent orchestrator  
  - MCP client for Todoist + Calendar
- **Integrations:**  
  - `mcp/todoist_server/`  
  - `mcp/calendar_server/` (new)

**Agent Flow:**
Chat → Backend Agent → MCP Client → MCP Servers (Todoist + Calendar)

css
Copy code

**Manual Flow:**
UI Actions → REST → Backend → MCP Client → MCP Servers

yaml
Copy code

---

## Scope

### Backend Extensions

#### New MCP Integration
Introduce a new MCP server:

- Folder: `mcp/calendar_server/`
- Capabilities:
  - `calendar.list_events`
  - `calendar.find_free_blocks`
  - `calendar.create_event`

Backend exposes **no direct API** for calendar integration; all calendar access goes through MCP.

#### Agent Extensions (LangGraph)
- Add task classification (atomic vs multi-step)
- Add scheduling logic:
  - Read calendar via MCP
  - Identify candidate admin blocks
  - Propose admin block in chat
- Introduce HITL:
  - Agent pauses when proposing a block  
  - Await approval from UI (Approvals tab)
- Guided execution mode:
  - Uses Todoist tasks via MCP
  - Presents tasks step-by-step during the approved block
  - Marks tasks complete via MCP

#### Backend REST Endpoints
- `/approvals/*` endpoints for controlling:
  - Approve calendar events
  - Reject proposals

- Endpoint that triggers guided session state transitions.

---

### Frontend Extensions

#### Approvals Tab
- Displays proposed admin blocks
- Buttons:
  - **Approve** → Backend → MCP → Calendar MCP server → create event
  - **Reject** → Backend clears proposal

#### Guided Execution Mode
- Activated when an admin block begins
- Chat transforms to:
  - “Task 1: …”
  - Buttons: Done / Skip / Next

UI state is driven by backend → MCP calls.

---

## Out of Scope (Phase 3)
- Gmail or email tools
- Multi-user hardening
- Complex priority algorithms
- Notifications beyond calendar events

---

## User Stories

1. Agent: “I suggest doing admin at 4pm today.”  
   → Proposal appears in Approvals tab.

2. Approve → Backend calls MCP → Calendar event created.

3. At the start of an admin block:
   - Guided mode activates.
   - One-task-at-a-time workflow appears.
   - Completing tasks updates Todoist through MCP.

4. Rejecting a proposal cancels it.

---

## Acceptance Criteria

- All calendar interactions route exclusively through MCP.
- No direct Google API usage in backend.
- Agent pauses appropriately for human approval.
- Guided mode reflects Todoist changes through MCP.
- Calendar and tasks remain consistent.
