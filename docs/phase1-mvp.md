# Phase 1 – MVP Specification

## Goal

Deliver the smallest viable version of Pushstart that **actually changes behaviour**
by:

- Letting the user add tasks quickly
- Classifying tasks simply (atomic vs multi-step)
- Proposing and creating daily admin blocks in the calendar
- Guiding the user through tasks during those blocks
- Keeping all external actions **human-in-the-loop (HITL)**

## Scope

### In Scope

- **Backend (FastAPI, Python)**
  - Task model + persistence (Postgres)
  - Basic REST endpoints:
    - `POST /tasks`
    - `GET /tasks`
  - Simple classification logic:
    - Atomic vs multi-step (rule-based and/or LLM-assisted)
  - Scheduling logic to:
    - Propose at least one daily admin block based on:
      - current tasks
      - simple time preferences
  - Orchestration endpoint(s) to:
    - Trigger “schedule admin block” agent workflow

- **Agent Layer**
  - LLM-based orchestration in Python
  - Uses MCP **calendar tool** only
    - Read availability
    - Propose admin block time
    - Create a block only after user approval
  - Basic reasoning rules:
    - Prefer short blocks (e.g. 10–20 minutes) over long ones
    - Avoid late-night scheduling
    - Respect user’s default working hours (configurable later)

- **Frontend (Next.js, TS)**
  - Simple UI to:
    - Add tasks
    - View list of tasks
    - See upcoming admin block(s)
    - Approve/reject proposed blocks

- **Guided Execution Mode (minimal)**
  - A very simple guided view for an active admin session:
    - Show “Current task”
    - Buttons: “Done”, “Skip”, “Next”
  - For Phase 1:
    - Assume atomic tasks only inside guided mode

- **HITL**
  - Any call that would lead to:
    - Creating a calendar block
    - Modifying or deleting a calendar block
  - must be **approved by the user** in the UI or via a confirmation endpoint.

### Out of Scope

- Email integration
- WhatsApp or messaging integrations
- Complex prioritisation algorithms
- Multi-user support
- Advanced UI/UX
- Deep-work sessions (can be Phase 2+)

## User Stories

1. **Task Capture**
   - As a user, I can add a task in a few seconds from the UI.
   - The task is saved and visible in a task list.

2. **Classification**
   - As a user, I can see whether a task is treated as “atomic” or “multi-step”.

3. **Scheduling Proposal**
   - As a user, I see a suggested admin block in the next 24 hours when there are pending tasks.
   - I can approve or reject the suggested block.

4. **Calendar Integration (MCP)**
   - When I approve a suggestion, the system creates a calendar event via the MCP calendar tool.
   - No event is created without my explicit approval.

5. **Guided Admin Session**
   - During an active admin block, I can open a simple guided view.
   - The system shows me one task at a time with basic “Done / Next / Skip”.

## Acceptance Criteria

- Tasks persist across server restarts.
- The system can propose at least one admin block per day when tasks exist.
- Calendar events are only created after user approval.
- Guided mode works for a list of atomic tasks:
  - Marking as done updates the backend.
- All calendar write operations are routed through a HITL flow.
