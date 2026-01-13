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
2. **Synthesizer**: Creates final actionable output

---

## Architecture

```
USER INPUT (Raw Idea)
        │
        ▼
┌─────────────────────────┐
│      MAIN AGENT         │
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
│ Return │  │ SYNTHESIZER│
│Questions│  │            │
│   ↓    │  │ Generate   │
│ Loop   │  │ Action Items│
└────────┘  └────────────┘
                 │
                 ▼
          FINAL OUTPUT
```

---

## Tech Stack
- **Language**: Python 3.11+
- **Framework**: FastAPI
- **LLM**: OpenAI GPT-4
- **Data Validation**: Pydantic

## Project Structure
```
Select_from_my_Ideas/
├── main.py              # CLI entry point
├── server.py            # Web server entry point
├── config.py            # Configuration management
├── agents/
│   ├── main_agent.py    # Main Agent
│   └── synthesizer.py   # Synthesizer Agent
├── models/              # Pydantic data models
├── services/
│   ├── orchestrator.py  # Conversation flow
│   └── llm_client.py    # LLM API wrapper
├── api/
│   └── routes.py        # FastAPI routes
├── prompts/             # Agent system prompts
└── database/            # Data persistence
```

---

## Core Data Flow

**Input** → Main Agent analyzes and generates questions
**User Selection** → Main Agent iterates or concludes
**Conclusion** → Synthesizer generates action items, tips, insights
