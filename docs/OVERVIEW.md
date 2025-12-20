# Pushstart – System Overview

Pushstart is a personal execution engine designed to remove **activation friction**
from life admin, follow-ups, and multi-step tasks.

Instead of being a generic “todo app,” Pushstart acts more like a
**personal chief of staff**:

1. Captures tasks from the user with minimal friction
2. Classifies and organises them
3. Schedules focused time blocks in the calendar
4. Guides the user step-by-step during those blocks
5. Uses external integrations via MCP tools
6. Keeps everything human-in-the-loop (HITL) for write actions

The initial target user is a single individual (Gaurav) with:

- High analytical ability
- Strong deep-work capability
- A tendency to avoid ambiguous, low-stimulation, administrivia-type tasks

## Core Concepts

- **Tasks:** Units of work captured by the user (e.g. “email X”, “apply for visa”)
- **Sessions:** Calendar blocks (e.g. daily admin, deep work) where tasks are executed
- **Guided Mode:** A step-by-step execution flow for sessions, driven by an agent
- **HITL:** No external action (email, calendar change, etc.) happens without user approval

## High-Level Architecture

### Frontend (Next.js, TypeScript)

- UI for:
  - Adding tasks
  - Viewing upcoming admin/deep-work sessions
  - Approving/rejecting suggestions
  - Running guided sessions (one step at a time)

### Backend (FastAPI, Python)

- **Core Responsibility:** Algorithms, Orchestration, and LLM/Agent Systems.
- **Location:** `backend/`
- REST API for:
  - Task CRUD (proxies to MCP + Cache)
  - Session data
  - User preferences/config
- Scheduling logic:
  - Decides when to propose new admin/deep-work blocks
- Orchestration endpoints:
  - Trigger agent workflows (e.g. “schedule admin blocks for next 24h”)

### Agent Layer (Python, LLM-based)

- Uses MCP tools to interact with external systems
- Responsibilities:
  - Task classification (atomic vs multi-step, etc.)
  - Proposing calendar sessions based on workload and preferences
  - Generating step-by-step guidance for sessions
  - Drafting external actions (emails, etc.) while remaining HITL

### Integrations via MCP

- **Core Design Principle:** All app integrations reside in the `mcp/` folder.
- The backend does **not** contain direct integration logic (e.g., Todoist API calls). It uses MCP clients to communicate with MCP servers.
- **Current Integrations:**
  - `mcp/todoist_server`: Manages tasks.
  - `mcp/calendar_server`: Manages events (Google Calendar).

Pushstart uses MCP tools which expose capabilities like:

- `todoist.list_tasks`, `todoist.create_task`, etc.
- `calendar.list_events`, `calendar.find_free_slots`, etc.

## Data & Caching Strategy

Since Pushstart relies heavily on external apps (Todoist, Google Calendar) as the source of truth, we implement a **Local PostgreSQL Cache** to ensure performance and stability.

### Cache Policy: Write-Through

- **Reads:** All read operations (e.g., listing tasks in the UI) are served directly from the **Local DB**. This ensures fast load times and offline capability.
- **Writes:** All write operations (Create, Update, Delete) follow a **Write-Through** pattern:
  1. **Write to External App:** The backend calls the MCP tool to perform the action on the external service (e.g., Todoist).
  2. **Update Local Cache:** Upon success, the local database is immediately updated to reflect the change.
- **Sync:** A "Full Sync" operation is available to reconcile any drift between the external app and the local cache (e.g., changes made directly in the Todoist app).

## Phases
**Phase 1 – Basic Todoist Integration (Completed)**
This phase established the foundational architecture with basic Todoist CRUD operations via MCP.

**Phase 2 – Agent Layer & Local Cache (Completed)**

We have successfully implemented the core agentic workflow and local caching layer.

**Key Achievements:**

- **LangGraph Agent:** A sophisticated agent that can manage tasks via natural language.
- **Human-in-the-Loop (HITL):** Sensitive actions (Create/Update/Delete) require explicit user approval via the UI.
- **Local PostgreSQL Cache:** Robust caching with Write-Through policy for Todoist tasks.
- **Chat Interface:** A rich chat UI with "Proposed Action" cards for HITL interactions.
- **Chat History:** Persistent chat sessions stored in Postgres.

**Phase 3 – Calendar Integration (Completed)**

We have successfully integrated Google Calendar via MCP and implemented scheduling logic.

**Key Achievements:**

- **Google Calendar MCP:** Full read/write access to calendar events via a dedicated MCP server.
- **Scheduling Logic:** The agent can find free slots and propose time blocks for tasks.
- **Guided Sessions:** (Foundation laid) The system can identify and work with scheduled blocks.
- **Unified MCP Architecture:** Both Todoist and Calendar are accessed strictly through MCP clients.

**Next Up: Advanced Orchestration & Multi-Modal Inputs**

- Email integration.
- Whatsapp integration.
- LinkedIn integration.
- More complex agentic workflows (e.g., "Plan my week").
- Voice input/output.
- Enhanced workflows for guided sessions.
- Deployment to cloud infrastructure.
- Android/iOS mobile app.
