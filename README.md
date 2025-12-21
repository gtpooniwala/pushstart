# Pushstart 🚀

**An agentic task manager that helps you actually execute tasks.**

Pushstart is not just another to-do list. It is a personal execution engine designed to overcome procrastination and decision fatigue. It turns vague intentions into scheduled, actionable sessions using AI agents and the Model Context Protocol (MCP).

## 🧠 Philosophy

Most productivity tools fail because they are just lists. They don't help you **start**.
Pushstart is built on three core principles:

1.  **Reduce Friction:** The agent handles the "admin" work—scheduling, prioritizing, and drafting emails—so you can focus on doing.
2.  **One Thing at a Time:** The system filters out noise and presents you with the single most important task to do *right now*.
3.  **Action over Planning:** Instead of asking "when do you want to do this?", Pushstart finds a slot and asks "Shall I book this for 2 PM?".

## ✨ Key Features

-   **🤖 Proactive Agent:** A LangGraph-based agent that manages your schedule and tasks. It doesn't just wait for commands; it makes decisions based on your priorities.
-   **🔗 MCP Integrations:** Built on the [Model Context Protocol](https://modelcontextprotocol.io/), Pushstart connects directly to your tools:
    -   **Todoist:** Two-way sync for task management.
    -   **Google Calendar:** Smart scheduling and free-slot finding.
    -   **Gmail:** Draft emails and summarize threads directly from the chat.
-   **🎯 Focus Mode:** A dedicated UI for executing tasks step-by-step without distractions.
-   **🔒 Privacy First:** Runs locally with your own API keys.

## 🛠️ Tech Stack

-   **Frontend:** Next.js 14, Tailwind CSS, Lucide Icons.
-   **Backend:** FastAPI, LangGraph (AI Orchestration), SQLAlchemy (Async).
-   **Integrations (MCP):** Python-based MCP servers for Todoist, Calendar, and Gmail.
-   **Infrastructure:** Docker (PostgreSQL), Conda (Python Environment).

## 🚀 Getting Started

### Prerequisites
-   Docker & Docker Compose
-   Conda (Miniconda/Anaconda)
-   Node.js & npm
-   **API Keys:**
    -   OpenAI API Key
    -   Todoist API Token
    -   Google Cloud Credentials (`credentials.json` for Calendar/Gmail)

### Installation

1.  **Clone the repo:**
    ```bash
    git clone https://github.com/gtpooniwala/pushstart.git
    cd pushstart
    ```

2.  **Setup Environment:**
    ```bash
    # Create .env file
    cp .env.example .env
    # Add your API keys to .env
    ```

3.  **Setup Google Credentials:**
    -   Place your `credentials.json` in `mcp/calendar_server/` and `mcp/gmail_server/`.

4.  **Run the Setup Script:**
    ```bash
    ./setup.sh
    ```

### Running the App

Start the entire stack (Frontend, Backend, Database, MCP Servers) with one command:

```bash
./run.sh
```

-   **Frontend:** [http://localhost:3000](http://localhost:3000)
-   **Backend Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)

## 📂 Project Structure

```
pushstart/
├── backend/          # FastAPI application & LangGraph Agent
├── frontend/         # Next.js application
├── mcp/              # Model Context Protocol Servers
│   ├── calendar_server/
│   ├── gmail_server/
│   └── todoist_server/
├── docs/             # Documentation
└── run.sh            # Main startup script
```

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.
