# Contributing Guidelines (Humans + Agents)

This project is currently single-user and under active development. Contributions
mainly come from the owner (Gaurav) and coding agents.

The goal is to keep the codebase **predictable, testable, and agent-friendly.**

---

## Repository Structure

- `backend/` – FastAPI, Python, Postgres access, orchestration endpoints
  - `app/` – application code (routers, services, models, agent)
  - `tests/` – backend tests

- `frontend/` – Next.js, TypeScript
  - `src/` – UI code
  - `tests/` – frontend tests

- `mcp/` – Model Context Protocol integrations
  - `todoist_server/` – Todoist integration
  - `calendar_server/` – Google Calendar integration
  - `tests/` – MCP tests

- `docs/` – documentation
- `scripts/` – helper scripts (dev, DB migrations, etc.)

---

## Branching Model

- `main` – always deployable / stable
- `feature/*` – branches for new features or changes

All work (including agent-generated changes) should be done in `feature/*` branches,
then merged to `main` via PR.

---

## Commit Style

Use clear, action-oriented messages, e.g.:

- `add basic task model and POST /tasks`
- `implement admin block proposal endpoint`
- `add MCP calendar client wrapper`

Avoid mixing unrelated changes in the same commit.

---

## Testing

- All non-trivial backend logic should have tests in `backend/tests`.
- Frontend components with logic should have tests in `frontend/tests`.

Before merging to `main`:

- Run backend tests
- Run frontend tests (once scaffolded)

---

## Linting / Formatting

- Python:
  - Use `black` + `isort` + `ruff` (to be wired later).
- TypeScript/JS:
  - Use `ESLint` + `Prettier`.

Formatting and linting can be enforced in CI gradually as the project stabilises.

---

## For Coding Agents

- Always read `docs/OVERVIEW.md` and `docs/phase1-mvp.md` before making
  architectural decisions.
- Follow `docs/AGENT_GUIDELINES.md` when writing code or orchestration logic.
- If a task is unclear:
  - Leave TODO comments and do not overcomplicate the implementation.
