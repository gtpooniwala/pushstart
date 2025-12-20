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
  - Chat interface for natural language interaction

- **Backend:** FastAPI (Python)  
  - **Core Logic:** Algorithms and LLM/Agent orchestration
  - **Data:** Local PostgreSQL cache for tasks and sessions
  - **API:** REST endpoints for frontend and agent triggers

- **Agent Layer:** Python LLM workflows (LangGraph)
  - Uses MCP tools to interact with external systems
  - Handles classification, step sequencing, and suggestions
  - Always respects HITL for write actions

- **Integrations:** MCP (Model Context Protocol)
  - All integrations live in the `mcp/` folder
  - **Todoist:** Two-way sync with local cache (Write-Through)
  - **Calendar:** Google Calendar integration for scheduling

## Current Stage

**Phase 2 – Agent Layer & Local Cache (Completed)**

We have implemented a sophisticated agentic workflow with a robust local caching layer.

**Key Features:**
- **Natural Language Interface:** Chat with the agent to manage tasks.
- **Local Cache:** Fast, offline-capable access to tasks via local Postgres DB.
- **Write-Through Sync:** Changes are pushed to Todoist and immediately reflected locally.
- **Human-in-the-Loop:** The agent proposes actions (create/update/delete), you approve them.

**Phase 3 – Calendar Integration (Completed)**

We have successfully integrated Google Calendar via MCP and implemented scheduling logic.

**Key Features:**
- **Google Calendar MCP:** Full read/write access to calendar events via a dedicated MCP server.
- **Scheduling Logic:** The agent can find free slots and propose time blocks for tasks.
- **Unified MCP Architecture:** Both Todoist and Calendar are accessed strictly through MCP clients.

**Next Up:** Phase 4 – Advanced Orchestration & Multi-Modal Inputs.

## Docs

- [Overview](docs/OVERVIEW.md)
- [Phase 1 MVP Spec](docs/phase1-mvp.md)
- [Agent Guidelines](docs/AGENT_GUIDELINES.md)
- [Contributing](CONTRIBUTING.md)

More setup and run instructions will be added as the backend/frontend are scaffolded.
