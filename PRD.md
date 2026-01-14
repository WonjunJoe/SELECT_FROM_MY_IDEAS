# Select From My Ideas

## Purpose
Transform raw, unstructured ideas into concrete, actionable outcomes through intelligent multi-turn conversations.

## Problem
People struggle to:
- Organize thoughts into actionable steps
- See concrete options from abstract ideas
- Make decisions when possibilities feel overwhelming

## Solution
A two-agent AI system:
1. **Main Agent**: Analyzes input, generates questions/options, decides when to conclude
2. **Synthesizer**: Creates final actionable output with personalized recommendations

---

## Architecture Overview

### System Flow
```
USER INPUT (Raw Idea) + UserProfile
        │
        ▼
┌─────────────────────────┐
│      ORCHESTRATOR       │ ← services/orchestrator.py
│  • Session management   │
│  • Agent routing        │
└─────────────────────────┘
        │
        ▼
┌─────────────────────────┐
│      MAIN AGENT         │ ← agents/main_agent.py
│  • Extract key info     │
│  • Generate questions   │
│  • Judge: continue/end  │
└─────────────────────────┘
        │
   ┌────┴────┐
   │         │
[continue]  [conclude]
   │         │
   ▼         ▼
┌────────┐  ┌────────────┐
│ Return │  │ SYNTHESIZER│ ← agents/synthesizer.py
│Questions│  │            │
│   ↓    │  │ Generate   │
│ Loop   │  │ Final Report│
└────────┘  └────────────┘
                 │
                 ▼
          FINAL OUTPUT
```

### Key Components

| Layer | Files | Description |
|-------|-------|-------------|
| **Entry Points** | `main.py`, `server.py` | CLI and Web API entry points |
| **Config** | `config.py` | Centralized settings from `.env` |
| **Agents** | `agents/main_agent.py`, `agents/synthesizer.py` | LLM-powered conversation agents |
| **Models** | `models/agent_io.py`, `models/session.py` | Pydantic data models |
| **Services** | `services/orchestrator.py`, `services/llm_client.py` | Business logic and LLM wrapper |
| **API** | `api/routes.py` | FastAPI REST endpoints |
| **Database** | `database/models.py`, `database/repository.py` | SQLite persistence via SQLAlchemy |
| **Logging** | `core/logging.py` | Structured logging system |
| **Prompts** | `prompts/*.txt` | Agent system prompts |
| **Frontend** | `frontend/index.html`, `frontend/app.js` | Web UI |

### Key Models

**UserProfile** (`models/agent_io.py`):
- `difficulty`: easy/medium/hard - determines response depth
- `age`, `gender`, `interests`: Required user info
- `job`, `goals`, `lifestyle`: Optional personalization

**MainAgentOutput** (`models/agent_io.py`):
- `understanding`: What user said, feels, values
- `summary`: Conversation summary
- `selections`: Questions with options for user
- `should_conclude`: Whether to end conversation

**FinalOutput** (`models/agent_io.py`):
- `original_input`: User's original query
- `user_profile`: User's profile information
- `final_summary`, `action_items`, `tips`, `insights`, `next_steps`, `encouragement`

**Session** (`models/session.py`):
- Tracks conversation state, rounds, user selections
- Persisted to SQLite via `database/models.py`

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/session/start` | Start new session with user input |
| POST | `/session/{id}/select` | Submit user selections |
| POST | `/session/{id}/end` | Force early conclusion |
| GET | `/session/{id}` | Get session state |
| GET | `/sessions` | List all sessions |
| DELETE | `/session/{id}` | Delete session |
| GET | `/health` | Health check |

---

## Tech Stack
- **Language**: Python 3.11+
- **Framework**: FastAPI
- **LLM**: OpenAI GPT-4o
- **Data Validation**: Pydantic
- **Database**: SQLite + SQLAlchemy
- **Logging**: structlog

## Project Structure
```
Select_from_my_Ideas/
├── main.py              # CLI entry point
├── server.py            # Web server entry point
├── config.py            # Configuration management
├── agents/
│   ├── base.py          # Base agent class
│   ├── main_agent.py    # Main Agent
│   └── synthesizer.py   # Synthesizer Agent
├── models/
│   ├── agent_io.py      # UserProfile, MainAgentOutput, FinalOutput
│   └── session.py       # Session, Round, UserSelection
├── services/
│   ├── orchestrator.py  # Conversation flow management
│   └── llm_client.py    # OpenAI API wrapper
├── api/
│   └── routes.py        # FastAPI routes
├── prompts/
│   ├── main_agent.txt   # Main Agent system prompt
│   └── synthesizer.txt  # Synthesizer system prompt
├── database/
│   ├── models.py        # SQLAlchemy ORM models
│   ├── repository.py    # Data access layer
│   └── connection.py    # DB connection management
├── core/
│   └── logging.py       # Logging configuration
├── frontend/
│   ├── index.html       # Web UI
│   ├── app.js           # Frontend logic
│   └── styles.css       # Styling
└── data/
    └── sessions.db      # SQLite database
```

---

## Update Log

### 2025-01-14
- **Show user context in final report**: Added `original_input` and `user_profile` fields to `FinalOutput` model. Final report now displays user's original query and profile at the top.

### 2025-01-13
- **Create User Profile**: Added `UserProfile` model with difficulty, age, gender, interests, job, goals, lifestyle fields for personalized responses
- **Update configs**: Simplified configuration and prompts
- **Update log architecture**: Improved structured logging system

### 2025-01-12
- **Create config system**: Centralized settings via `config.py` and `.env`
- **Create db system**: SQLite persistence with SQLAlchemy ORM
- **Create log system**: Structured logging with file and console output

### 2025-01-11
- **Try front-end**: Added web UI with `frontend/index.html`, `app.js`, `styles.css`
- **Update README.md**: Documentation for setup and usage

### 2025-01-10
- **Improvement of prompts**: Enhanced agent prompts for higher specificity and better responses

### 2025-01-09
- **Initial project setup**: Two-agent architecture (Main Agent + Synthesizer), CLI interface, FastAPI server, Pydantic models
