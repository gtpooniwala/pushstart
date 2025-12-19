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
- REST API for:
  - Task CRUD
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

Pushstart does **not** talk directly to external APIs inside core logic.
Instead, it uses MCP tools, which expose capabilities like:

- `calendar.list_events`
- `calendar.find_free_slots`
- `calendar.propose_block`
- `calendar.create_block` (HITL-gated)

Later phases can add MCP tools for:
- Email (draft/send/reply)
- Messaging platforms
- Notion or other task/knowledge sources

## Current Phase

**Phase 2 – Agent Layer & Local Cache**

The focus of Phase 2 is to:
- Introduce a LangGraph-based Agent for natural language task management.
- Implement a **Local PostgreSQL Cache** for tasks to improve performance and stability.
- Enforce a **Write-Through Cache Policy** (Write to Todoist -> Update Local DB).
- Enhance the Frontend with a Chat Interface and "Proposed Action" approvals (HITL).
- Prepare the system for Phase 3 (Calendar Integration).

**Completed in Phase 2:**
- LangGraph Agent with HITL for sensitive tools.
- Local PostgreSQL Database (Docker).
- TaskService for unified cache management.
- Frontend Chat UI with diff-based approvals.

**Pending in Phase 2:**
- Chat History persistence.
- Sidebar workflow selection.
