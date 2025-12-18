# Pushstart

Pushstart is a personal execution engine that turns vague intentions and tasks
into **scheduled, guided sessions** in your calendar.

Instead of relying on motivation or willpower, Pushstart:

- Captures tasks quickly
- Classifies and organises them
- Schedules focused “admin” and “deep work” blocks
- Guides you step-by-step during those blocks
- Uses external integrations via MCP tools (calendar now, more later)
- Keeps all external actions **human-in-the-loop (HITL)**

The primary user is a single individual (Gaurav) who:
- Avoids ambiguous, low-stimulation tasks
- Responds well to clear structure and guided steps
- Wants the system to reduce friction, not create more work

## Architecture (High Level)

- **Frontend:** Next.js (TypeScript)  
  - UI for viewing tasks, reviewing suggestions, and running guided sessions  

- **Backend:** FastAPI (Python)  
  - Task storage (Postgres)
  - Scheduling logic (when/where to place sessions on the calendar)
  - REST API for the frontend
  - Orchestration endpoints for agent workflows

- **Agent Layer:** Python LLM workflows  
  - Uses MCP tools to interact with external systems (calendar now, email/others later)
  - Handles classification, step sequencing, and suggestions
  - Always respects HITL for write actions

- **Integrations:** MCP tools  
  - Phase 1: Calendar tool for reading availability and creating “admin blocks”
  - Later: email, messaging, task source tools

## Current Stage

**Phase 1 – Calendar-Based HITL MVP**

Focus:
- Manual task input
- Simple classification (atomic vs multi-step)
- Calendar-driven daily admin blocks
- Guided execution mode inside those blocks
- All external actions ask for confirmation

## Docs

- [Overview](docs/OVERVIEW.md)
- [Phase 1 MVP Spec](docs/phase1-mvp.md)
- [Agent Guidelines](docs/AGENT_GUIDELINES.md)
- [Contributing](CONTRIBUTING.md)

More setup and run instructions will be added as the backend/frontend are scaffolded.
