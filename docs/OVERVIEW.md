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

**Phase 1 – Calendar-Based MVP**

The focus of Phase 1 is to:
- Build the core backend & frontend skeleton
- Implement manual task input
- Use the agent + MCP calendar tool to propose and schedule **daily admin blocks**
- Implement a basic guided execution mode for admin sessions
- Enforce HITL for all calendar writes
