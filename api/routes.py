"""
FastAPI routes for Select From My Ideas
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import os

from models import UserSelection, FinalOutput
from services.orchestrator import Orchestrator

app = FastAPI(title="Select From My Ideas API")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session storage (for MVP)
sessions: dict[str, Orchestrator] = {}


# Request/Response Models
class StartSessionRequest(BaseModel):
    input: str


class SelectionInput(BaseModel):
    question: str
    selected_option: Optional[str] = None
    custom_input: Optional[str] = None


class SubmitSelectionsRequest(BaseModel):
    selections: list[SelectionInput]


class SelectionResponse(BaseModel):
    question: str
    options: list[str]
    allow_other: bool


class SessionResponse(BaseModel):
    session_id: str
    summary: str
    selections: list[SelectionResponse]
    should_conclude: bool
    final_output: Optional[dict] = None


# Routes
@app.post("/session/start", response_model=SessionResponse)
async def start_session(request: StartSessionRequest):
    """Start a new session with user's raw idea."""
    try:
        orchestrator = Orchestrator()
        output = orchestrator.start_session(request.input)

        session_id = orchestrator.session.session_id
        sessions[session_id] = orchestrator

        if output.should_conclude:
            # Immediately conclude (rare case)
            final = orchestrator.process_selections([])
            return SessionResponse(
                session_id=session_id,
                summary=output.summary,
                selections=[],
                should_conclude=True,
                final_output=final.model_dump() if isinstance(final, FinalOutput) else None,
            )

        return SessionResponse(
            session_id=session_id,
            summary=output.summary,
            selections=[
                SelectionResponse(
                    question=s.question,
                    options=s.options,
                    allow_other=s.allow_other,
                )
                for s in output.selections
            ],
            should_conclude=False,
        )
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/session/{session_id}/select", response_model=SessionResponse)
async def submit_selections(session_id: str, request: SubmitSelectionsRequest):
    """Submit user selections and get next response."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    orchestrator = sessions[session_id]

    user_selections = [
        UserSelection(
            question=sel.question,
            selected_option=sel.selected_option,
            custom_input=sel.custom_input,
        )
        for sel in request.selections
    ]

    result = orchestrator.process_selections(user_selections)

    if isinstance(result, FinalOutput):
        # Clean up session after completion
        del sessions[session_id]
        return SessionResponse(
            session_id=session_id,
            summary="",
            selections=[],
            should_conclude=True,
            final_output=result.model_dump(),
        )

    return SessionResponse(
        session_id=session_id,
        summary=result.summary,
        selections=[
            SelectionResponse(
                question=s.question,
                options=s.options,
                allow_other=s.allow_other,
            )
            for s in result.selections
        ],
        should_conclude=result.should_conclude,
    )


@app.get("/session/{session_id}")
async def get_session(session_id: str):
    """Get current session state."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    orchestrator = sessions[session_id]
    session = orchestrator.get_session()

    return {
        "session_id": session.session_id,
        "status": session.status,
        "current_round": session.current_round,
        "original_input": session.original_input,
    }


# Serve frontend static files
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")


@app.get("/")
async def serve_frontend():
    """Serve the frontend index.html."""
    return FileResponse(os.path.join(frontend_path, "index.html"))


# Mount static files for CSS and JS
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
