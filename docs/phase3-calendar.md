# Phase 3 – Calendar, Scheduling, and Guided Execution (MCP-First)

## Goal

Transform Pushstart into a true productivity assistant by adding:

- Calendar integration through a **Google Calendar MCP server**
- Scheduling logic (admin block proposals)
- HITL approvals for all calendar writes
- Guided execution mode during approved admin blocks

Todoist and Calendar are both fully MCP-based.

---

## Architecture Overview

- **Frontend:** Chat + Right Panel + Approvals Tab + Guided Mode
- **Backend:** FastAPI + LangGraph agent
- **Integrations:**  
  - Todoist MCP server  
  - Calendar MCP server (new)

### Data Flow

Agent:
Chat → Backend Agent → MCP Client (Todoist/Calendar) → MCP Servers

makefile
Copy code
Manual:
UI → REST → Backend → MCP Client → MCP Servers

yaml
Copy code

### Architectural Principle

The backend continues to be the **sole MCP client**.  
Agent nodes and REST handlers share the same MCP client modules:

- `backend/mcp_client/todoist_client.py`
- `backend/mcp_client/calendar_client.py`

---

## Scope

### Backend Extensions

#### New MCP Integration

Add `mcp/calendar_server/` implementing tools:

- `calendar.list_events`
- `calendar.find_free_blocks`
- `calendar.create_event`

Backend uses a new MCP client module:

- `backend/mcp_client/calendar_client.py`

No direct Google API calls in backend.

#### Agent Extensions (LangGraph)

- Task classification (atomic vs multi-step)
- Scheduling logic:
  - Read events via MCP
  - Identify candidate admin blocks
  - Propose a block in chat
- HITL approval:
  - Agent pauses until frontend approves/rejects
  - After approval → agent calls `calendar.create_event` via MCP
- Guided mode logic:
  - On block start, agent enters guided state
  - Iterates through Todoist tasks via MCP
  - Marks completed tasks via MCP

#### Backend REST Endpoints

- `/approvals/*` for approving/rejecting block proposals
- `/guided/*` for guided session transitions

---

### Frontend Extensions

#### Approvals Tab

- Shows proposed admin blocks
- User selects:
  - **Approve** → backend → MCP → calendar event created
  - **Reject**

#### Guided Execution Mode

- Activated at admin block start
- Shows:
  - Current task
  - Controls: Done / Skip / Next
- Driven entirely by backend agent state

---

## Out of Scope (Phase 3)

- Gmail integration
- Notifications (outside calendar)
- Multi-user support
- Advanced prioritisation algorithms

---

## User Stories

1. Agent: “I suggest doing admin at 4pm today.”
   → Proposal appears in Approvals tab.
2. Approve → calendar event created through MCP.
3. Admin block starts → guided mode begins.
4. Tasks are presented one by one and updated via MCP.
5. Rejecting a block cancels the proposal.

---

## Acceptance Criteria

- All Todoist and Calendar access flows through MCP only.
- Agent pauses correctly for HITL.
- Guided mode operates deterministically.
- Todoist and Calendar remain consistent with agent actions.
