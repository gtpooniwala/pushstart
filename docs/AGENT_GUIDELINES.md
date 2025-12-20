# Agent Coding & Behaviour Guidelines for Pushstart

These guidelines describe how LLM-based agents (including coding agents and
orchestration agents) should behave when working on Pushstart.

---

## General Principles

- Maintain **clarity**, use **small composable functions**, and avoid over-design.
- Respect the existing architecture and folder structure.
- Prefer explicit logic over magic or heavy abstractions.
- All external-facing operations must remain **human-in-the-loop (HITL)**.

---

## Coding Agents (implementing features)

When implementing or modifying code:

1. **Read Before Writing**
   - Read the full file before editing it.
   - Respect existing naming conventions and patterns.

2. **Keep Changes Local**
   - Avoid global refactors unless explicitly requested.
   - Do not mix unrelated features or fixes in the same change.

3. **Tests**
   - Add or update tests when changing behaviour.
   - Keep backend tests in `backend/tests` and frontend tests in `frontend/tests`.

4. **Dependencies**
   - Do not add new dependencies without clear justification.
   - Prefer using existing libraries and patterns already in the project.

5. **Pull Requests**
   - Include a short summary of the change.
   - Link to the relevant issue.
   - Indicate what tests were run.

---

## Orchestration Agents (runtime behaviour)

When orchestrating tasks and interacting with external systems:

1. **Use MCP Tools for Integrations**
   - All calendar access should go through the MCP calendar tool.
   - Future integrations (email, messaging, etc.) will also be exposed as MCP tools.
   - **Do not** attempt to call external APIs directly.

2. **Rely on Service Layer for Data**
   - The `TaskService` and other services handle caching and synchronization.
   - Assume that `list_tasks` returns data from the local cache (fast).
   - Assume that `create_task` and other mutations are write-through (update external app + local cache).

3. **Human-in-the-Loop (HITL)**
   - Sensitive actions (Create, Update, Delete) are intercepted by the system for user approval.
   - The agent should propose these actions, but not assume they are executed until confirmed.
   - Do not call external APIs directly from orchestration logic.

2. **HITL for Writes**
   - Never perform calendar write actions (create/update/delete events) without
     explicit confirmation from the user.
   - Propose actions first, then wait for an “approved” signal from the backend/UI.

3. **Calendar Behaviour**
   - Prefer short admin blocks (e.g. 10–20 minutes) when uncertain.
   - Avoid scheduling blocks during late-night hours unless explicitly configured.
   - Label events clearly (e.g. `Pushstart – Admin`).

4. **Task Handling**
   - For Phase 1, treat tasks as:
     - `atomic` (can be done in one step)
     - `multi_step` (requires later workflows, but still stored)
   - Do not overcomplicate classification in Phase 1.

5. **Guided Sessions**
   - Show one task at a time.
   - Support simple actions: done, skip, next.
   - Keep instructions concise and concrete.

6. **Ambiguity**
   - If requirements are ambiguous, leave clear TODO comments or logs for human review
     rather than guessing complex behaviour.

---

These guidelines will evolve as Pushstart grows, but the core principles of
HITL, MCP-based integration, and clarity-first design should remain stable.
