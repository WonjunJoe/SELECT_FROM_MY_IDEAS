# PRD: Select From My Ideas

## Overview

**Product Name:** Select From My Ideas

**Version:** 1.0

**Last Updated:** 2025-01-12

### Vision
Transform raw, unstructured ideas into concrete, actionable outcomes through intelligent multi-turn conversations that progressively clarify and refine user thoughts.

### Problem Statement
People often have vague ideas, scattered thoughts, or abstract concepts but struggle to:
- Organize thoughts into actionable steps
- See concrete options from abstract ideas
- Make decisions when possibilities feel overwhelming
- Know when they've thought through something enough

### Solution
A two-agent AI system that:
1. **Main Agent**: Analyzes input, generates questions/options, and decides when to conclude
2. **Synthesizer**: Creates final actionable output when ready

---

## System Architecture

### Simplified Two-Agent Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER INPUT (Raw Idea)                        │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │                               │
                    │     MAIN AGENT (메인 에이전트)  │
                    │                               │
                    │  • Extract key information    │
                    │  • Generate questions/options │
                    │  • Track conversation context │
                    │  • Judge: continue or conclude│
                    │                               │
                    └───────────────────────────────┘
                                    │
                          ┌────────┴────────┐
                          │                 │
                   [should_conclude:    [should_conclude:
                        false]              true]
                          │                 │
                          ▼                 ▼
                  ┌──────────────┐   ┌─────────────────────────┐
                  │    Return    │   │   SYNTHESIZER (종합기)   │
                  │   Questions  │   │                         │
                  │   & Options  │   │  • Analyze full context │
                  │      ↓       │   │  • Generate action items│
                  │ User Selects │   │  • Provide tips/insights│
                  │      ↓       │   │                         │
                  │ Loop back to │   └─────────────────────────┘
                  │  Main Agent  │               │
                  └──────────────┘               ▼
                                    ┌─────────────────────────┐
                                    │      FINAL OUTPUT       │
                                    └─────────────────────────┘
```

## Agent Specifications

### Main Agent (메인 에이전트)

**Role:** Handle all conversation logic in a single agent

**Input:**
```json
{
  "original_input": "유저의 최초 raw input",
  "conversation_history": [
    {
      "round": 1,
      "summary": "이전 라운드 요약",
      "questions": [...],
      "user_selections": [...]
    }
  ],
  "current_round": 2
}
```

**Responsibilities:**
1. **First Round (Extract)**
   - Parse raw input
   - Identify themes, goals, problems
   - Generate initial questions/options

2. **Subsequent Rounds (Iterate)**
   - Integrate new selections with context
   - Update understanding
   - Generate next questions/options

3. **Every Round (Judge)**
   - Evaluate if enough clarity achieved
   - Decide: continue or conclude
   - Output `should_conclude` flag

**Output:**
```json
{
  "understanding": {
    "main_themes": ["테마1", "테마2"],
    "user_intent": "유저의 의도",
    "clarified_points": ["명확해진 것들"],
    "remaining_uncertainties": ["아직 불명확한 것들"]
  },
  "summary": "현재까지의 대화 요약",
  "selections": [
    {
      "question": "질문",
      "options": ["선택지1", "선택지2", "선택지3"],
      "allow_other": true
    }
  ],
  "should_conclude": false,
  "conclusion_reason": null
}
```

**Conclusion Criteria:**
```
should_conclude = true IF:
  - current_round >= 5 (max iterations)
  - OR remaining_uncertainties is empty/minimal
  - OR user intent is clear AND actionable
  - OR information_gain from last round < threshold
```

---

### Synthesizer (종합기)

**Role:** Generate final, actionable output

**Input:**
```json
{
  "original_input": "최초 raw input",
  "conversation_history": [...],
  "final_understanding": {
    "main_themes": [...],
    "user_intent": "...",
    "clarified_points": [...]
  }
}
```

**Output:**
```json
{
  "final_summary": "전체 대화 요약",
  "action_items": [
    {
      "action": "구체적 행동",
      "priority": "high" | "medium" | "low",
      "effort": "minimal" | "moderate" | "significant"
    }
  ],
  "tips": ["실용적 팁1", "실용적 팁2"],
  "insights": ["개인화된 인사이트1", "개인화된 인사이트2"],
  "next_steps": "추천하는 다음 단계",
  "encouragement": "응원 메시지"
}
```

---

## Complete Example Flow

### Round 1 (Main Agent - First Contact)

**User Input:**
```
최소단위를 만들어 놓고 그것만 해보자 예) 운동 - 헬스장만 가자, 옷만 입고 10분 있어보자 등.
새로운 아이디어로 템플릿에서 선택할 수 있게 하는거야. 결국 선택이 이길 것 같음.
```

**Main Agent Output:**
```json
{
  "understanding": {
    "main_themes": ["최소단위 행동", "습관 형성", "선택 기반 시스템"],
    "user_intent": "작은 행동으로 시작해서 실행력을 높이고 싶음 + 이를 서비스화하고 싶음",
    "clarified_points": ["최소단위 개념 이해", "운동 예시 있음"],
    "remaining_uncertainties": ["적용할 구체적 영역", "서비스 아이디어 구체화 여부"]
  },
  "summary": "당신은 '최소단위 행동'으로 실행력을 높이는 방법을 생각하고 계시고, 이를 '선택' 메커니즘과 결합한 서비스 아이디어도 가지고 계시네요!",
  "selections": [
    {
      "question": "어떤 영역에서 먼저 최소단위 행동을 시작해보고 싶으세요?",
      "options": [
        "운동/건강 - 헬스장 가기, 스트레칭 등",
        "학습/자기개발 - 책 읽기, 공부 등",
        "창작/취미 - 음악, 글쓰기, 그림 등",
        "생산성/업무 - 할일 관리, 집중 등"
      ],
      "allow_other": true
    },
    {
      "question": "'선택 기반 템플릿' 아이디어도 발전시켜볼까요?",
      "options": [
        "네, 이 아이디어를 구체화하고 싶어요",
        "아니요, 일단 제 행동 실천에 집중할래요",
        "둘 다 동시에 진행하고 싶어요"
      ],
      "allow_other": true
    }
  ],
  "should_conclude": false,
  "conclusion_reason": null
}
```

---

### Round 2 (Main Agent - Iterate)

**User Selection:**
- Q1: "운동/건강"
- Q2: "네, 이 아이디어를 구체화하고 싶어요"

**Main Agent Output:**
```json
{
  "understanding": {
    "main_themes": ["운동 습관", "선택 기반 서비스"],
    "user_intent": "운동에서 최소단위 행동 실천 + 서비스 아이디어 구체화",
    "clarified_points": ["운동 영역 선택", "서비스 아이디어 관심 확인"],
    "remaining_uncertainties": ["구체적 최소단위 행동 정의", "서비스 형태"]
  },
  "summary": "운동 영역에서 최소단위 행동을 시작하시고, 선택 기반 서비스 아이디어도 구체화하고 싶으시군요!",
  "selections": [
    {
      "question": "운동에서 당신만의 '최소단위 행동'은 무엇인가요?",
      "options": [
        "운동복 입기 (일단 옷만 갈아입기)",
        "헬스장 도착하기 (운동 안해도 OK)",
        "5분만 움직이기 (뭐든 5분)"
      ],
      "allow_other": true
    },
    {
      "question": "'선택 기반 서비스'는 어떤 형태를 상상하시나요?",
      "options": [
        "앱/웹에서 버튼으로 선택하는 형태",
        "챗봇이 선택지를 제안해주는 형태",
        "미리 정해둔 리스트에서 고르는 형태"
      ],
      "allow_other": true
    }
  ],
  "should_conclude": false,
  "conclusion_reason": null
}
```

---

### Round 3 (Main Agent - Conclude)

**User Selection:**
- Q1: "운동복 입기"
- Q2: "챗봇이 선택지를 제안해주는 형태"

**Main Agent Output:**
```json
{
  "understanding": {
    "main_themes": ["운동 습관", "챗봇 서비스"],
    "user_intent": "운동복 입기를 최소단위로 실천 + 챗봇 형태의 선택 서비스 개발",
    "clarified_points": [
      "최소단위: 운동복 입기",
      "서비스 형태: 챗봇",
      "핵심 가치: 선택으로 실행력 높이기"
    ],
    "remaining_uncertainties": []
  },
  "summary": "명확해졌습니다! '운동복 입기'를 최소단위로 운동을 시작하시고, '챗봇이 선택지를 제안하는' 서비스를 만들고 싶으시네요.",
  "selections": [],
  "should_conclude": true,
  "conclusion_reason": "User intent is clear and actionable. All key decisions made."
}
```

---

### Final (Synthesizer)

**Synthesizer Output:**
```json
{
  "final_summary": "당신은 '최소단위 행동(운동복 입기)'으로 운동 습관을 만들고, 이 개념을 '챗봇 기반 선택 서비스'로 발전시키고 싶어하시네요.",

  "action_items": [
    {
      "action": "내일부터 '운동복 입기'만 목표로 시작하기",
      "priority": "high",
      "effort": "minimal"
    },
    {
      "action": "1주일 실천 후 다음 단계(헬스장 가기)로 확장",
      "priority": "medium",
      "effort": "minimal"
    },
    {
      "action": "챗봇 서비스 아이디어를 노트에 정리하기",
      "priority": "medium",
      "effort": "moderate"
    },
    {
      "action": "간단한 프로토타입(카카오톡 챗봇 등) 구상해보기",
      "priority": "low",
      "effort": "moderate"
    }
  ],

  "tips": [
    "최소단위는 '실패할 수 없을 정도로 작게' - 운동복 입고 다시 벗어도 성공!",
    "streak보다 '다시 시작하기'에 집중하세요",
    "챗봇 MVP는 단순하게 - 3개 선택지면 충분해요"
  ],

  "insights": [
    "'선택'이 '의지력'보다 강하다는 통찰이 서비스의 핵심 가치가 될 수 있어요",
    "당신이 직접 실천하면서 얻는 경험이 서비스 설계에 가장 좋은 인풋이 됩니다"
  ],

  "next_steps": "이번 주: 운동복 입기 실천 (매일 기록)\n주말: 챗봇 아이디어 30분 정리",

  "encouragement": "작게 시작하는 것의 힘을 아는 당신이라면 분명 해낼 수 있어요!"
}
```

---

## Data Models

### Session
```python
@dataclass
class Session:
    session_id: str
    created_at: datetime
    original_input: str
    conversation_history: List[Round]
    current_round: int
    status: Literal["in_progress", "completed"]
    final_output: Optional[FinalOutput]
```

### Round
```python
@dataclass
class Round:
    round_number: int
    agent_output: MainAgentOutput
    user_selections: List[UserSelection]
```

### UserSelection
```python
@dataclass
class UserSelection:
    question: str
    selected_option: Optional[str]
    custom_input: Optional[str]  # When "기타" selected
```

### MainAgentOutput
```python
@dataclass
class MainAgentOutput:
    understanding: Understanding
    summary: str
    selections: List[Selection]
    should_conclude: bool
    conclusion_reason: Optional[str]
```

### FinalOutput
```python
@dataclass
class FinalOutput:
    final_summary: str
    action_items: List[ActionItem]
    tips: List[str]
    insights: List[str]
    next_steps: str
    encouragement: str
```

---

## Technical Architecture

### System Components

```
┌──────────────────────────────────────────────────────────────────┐
│                        Client Layer                               │
│                  (CLI → Web → Mobile Future)                      │
└──────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────┐
│                      API Layer (FastAPI)                          │
│  POST /session/start       - Start new session (first input)     │
│  POST /session/{id}/select - Submit user selection               │
│  GET  /session/{id}        - Get current session state           │
└──────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────┐
│                    Orchestrator Service                           │
│  • Manages session state                                          │
│  • Routes to Main Agent or Synthesizer                           │
│  • Handles conversation flow                                      │
└──────────────────────────────────────────────────────────────────┘
                                │
                ┌───────────────┴───────────────┐
                ▼                               ▼
        ┌─────────────┐                 ┌─────────────┐
        │ Main Agent  │                 │ Synthesizer │
        └─────────────┘                 └─────────────┘
                │                               │
                └───────────────┬───────────────┘
                                ▼
                    ┌─────────────────────┐
                    │    LLM Provider     │
                    │  (OpenAI / Claude)  │
                    └─────────────────────┘
```

### Tech Stack
- **Language:** Python 3.11+
- **Framework:** FastAPI
- **LLM:** OpenAI GPT-4 or Anthropic Claude
- **State Management:** In-memory dict (MVP) → Redis (Production)
- **Data Validation:** Pydantic

### Project Structure
```
Select_from_my_Ideas/
├── main.py                 # Entry point (CLI for MVP)
├── requirements.txt
├── .env                    # API keys (OPENAI_API_KEY or ANTHROPIC_API_KEY)
├── .gitignore
├── PRD.md
│
├── agents/
│   ├── __init__.py
│   ├── base.py             # Base agent class
│   ├── main_agent.py       # Main Agent (extract + iterate + judge)
│   └── synthesizer.py      # Synthesizer Agent
│
├── models/
│   ├── __init__.py
│   ├── session.py          # Session, Round dataclasses
│   ├── agent_io.py         # Agent input/output models
│   └── selection.py        # Selection models
│
├── services/
│   ├── __init__.py
│   ├── orchestrator.py     # Conversation flow management
│   └── llm_client.py       # LLM API wrapper
│
├── prompts/
│   ├── main_agent.txt      # Main Agent system prompt
│   └── synthesizer.txt     # Synthesizer system prompt
│
└── api/                    # Phase 2
    ├── __init__.py
    └── routes.py           # FastAPI routes
```

---

## Development Phases

### Phase 1: Core MVP (CLI)
- [ ] Set up project structure
- [ ] Implement LLM client wrapper (OpenAI or Claude)
- [ ] Write Main Agent prompt
- [ ] Write Synthesizer prompt
- [ ] Build Main Agent class
- [ ] Build Synthesizer class
- [ ] Create Orchestrator service
- [ ] Build CLI interface
- [ ] End-to-end testing with sample inputs

### Phase 2: API Layer
- [ ] Implement FastAPI routes
- [ ] Add session management (in-memory)
- [ ] Error handling & validation
- [ ] Request/response logging

### Phase 3: Web Interface
- [ ] Simple web UI
- [ ] Real-time conversation display
- [ ] Selection buttons/forms
- [ ] Mobile responsive

### Phase 4: Production Ready
- [ ] Redis for session storage
- [ ] Rate limiting
- [ ] Prompt optimization
- [ ] Monitoring & analytics

---

## API Endpoints (Phase 2)

### POST /session/start
Start a new session with raw input.

**Request:**
```json
{
  "input": "유저의 raw idea"
}
```

**Response:**
```json
{
  "session_id": "uuid",
  "summary": "...",
  "selections": [...],
  "should_conclude": false
}
```

### POST /session/{id}/select
Submit user's selection and get next response.

**Request:**
```json
{
  "selections": [
    {"question": "Q1", "selected_option": "Option A"},
    {"question": "Q2", "custom_input": "사용자 입력"}
  ]
}
```

**Response (if should_conclude: false):**
```json
{
  "summary": "...",
  "selections": [...],
  "should_conclude": false
}
```

**Response (if should_conclude: true):**
```json
{
  "final_output": {
    "final_summary": "...",
    "action_items": [...],
    "tips": [...],
    "insights": [...],
    "next_steps": "...",
    "encouragement": "..."
  }
}
```

### GET /session/{id}
Get current session state.

---

## Success Metrics

| Metric | Target | Description |
|--------|--------|-------------|
| Completion Rate | > 80% | Sessions reaching final output |
| Avg Rounds | 3-4 | Rounds needed to conclude |
| Response Time | < 3s | Per LLM call |
| User Satisfaction | > 4/5 | Output helpfulness rating |

---

## Constraints & Considerations

- **Token Efficiency:** Single Main Agent reduces context duplication
- **Latency:** Target < 3 seconds per response
- **Language:** Korean + English natural support
- **Cost:** ~5 LLM calls per session (vs 8 in 4-agent design)
- **Context Window:** Keep conversation history concise to fit in context
