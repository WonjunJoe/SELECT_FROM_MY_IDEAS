"""
FastAPI routes for Select From My Ideas
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import os
import time

from models import UserSelection, FinalOutput
from services.orchestrator import Orchestrator
from core.logging import logger

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


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests."""
    start_time = time.time()

    # Log request
    logger.info(
        f"Request: {request.method} {request.url.path}",
        method=request.method,
        path=request.url.path,
        client=request.client.host if request.client else "unknown",
    )

    try:
        response = await call_next(request)
        elapsed = time.time() - start_time

        logger.info(
            f"Response: {request.method} {request.url.path} -> {response.status_code}",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            elapsed_ms=round(elapsed * 1000, 2),
        )
        return response
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(
            f"Request failed: {request.method} {request.url.path}",
            method=request.method,
            path=request.url.path,
            error=str(e),
            elapsed_ms=round(elapsed * 1000, 2),
        )
        raise


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
    logger.info(
        "Starting new session",
        input_length=len(request.input),
        input_preview=request.input[:100] + "..." if len(request.input) > 100 else request.input,
    )

    try:
        orchestrator = Orchestrator()
        output = orchestrator.start_session(request.input)

        session_id = orchestrator.session.session_id
        sessions[session_id] = orchestrator

        logger.info(
            f"Session created: {session_id}",
            session_id=session_id,
            num_questions=len(output.selections),
            should_conclude=output.should_conclude,
        )

        if output.should_conclude:
            logger.info(f"Session {session_id} concluding immediately")
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
        logger.error(f"Failed to start session: {e}", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/session/{session_id}/select", response_model=SessionResponse)
async def submit_selections(session_id: str, request: SubmitSelectionsRequest):
    """Submit user selections and get next response."""
    logger.info(
        f"Processing selections for session {session_id}",
        session_id=session_id,
        num_selections=len(request.selections),
    )

    if session_id not in sessions:
        logger.warning(f"Session not found: {session_id}")
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

    # Log user selections
    for sel in user_selections:
        logger.debug(
            f"User selection: {sel.question[:50]}...",
            question=sel.question,
            selected_option=sel.selected_option,
            custom_input=sel.custom_input,
        )

    result = orchestrator.process_selections(user_selections)

    if isinstance(result, FinalOutput):
        logger.info(
            f"Session {session_id} completed",
            session_id=session_id,
            num_action_items=len(result.action_items),
        )
        # Clean up session after completion
        del sessions[session_id]
        return SessionResponse(
            session_id=session_id,
            summary="",
            selections=[],
            should_conclude=True,
            final_output=result.model_dump(),
        )

    logger.info(
        f"Session {session_id} continuing to next round",
        session_id=session_id,
        current_round=orchestrator.session.current_round,
        num_questions=len(result.selections),
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
    logger.debug(f"Getting session state: {session_id}")

    if session_id not in sessions:
        logger.warning(f"Session not found: {session_id}")
        raise HTTPException(status_code=404, detail="Session not found")

    orchestrator = sessions[session_id]
    session = orchestrator.get_session()

    return {
        "session_id": session.session_id,
        "status": session.status,
        "current_round": session.current_round,
        "original_input": session.original_input,
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "active_sessions": len(sessions),
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


# Startup event
@app.on_event("startup")
async def startup_event():
    """Log application startup."""
    logger.info("FastAPI application started")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Log application shutdown."""
    logger.info(f"FastAPI application shutting down. Active sessions: {len(sessions)}")
