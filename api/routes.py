"""
FastAPI routes for Select From My Ideas
"""

from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session
import os
import time

from models import UserSelection, FinalOutput
from services.orchestrator import Orchestrator
from database import init_db, SessionRepository
from database.connection import get_db_session
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

# In-memory orchestrator cache (for active sessions)
orchestrators: dict[str, Orchestrator] = {}


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests."""
    start_time = time.time()

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
class UserProfileInput(BaseModel):
    """User profile for personalized responses."""
    difficulty: str  # easy, medium, hard
    age: int
    gender: str
    interests: List[str]
    job: Optional[str] = None
    goals: Optional[str] = None
    lifestyle: Optional[str] = None


class StartSessionRequest(BaseModel):
    input: str
    user_profile: Optional[UserProfileInput] = None


class SelectionInput(BaseModel):
    question: str
    selected_option: Optional[str] = None
    custom_input: Optional[str] = None


class SubmitSelectionsRequest(BaseModel):
    selections: List[SelectionInput]


class SelectionResponse(BaseModel):
    question: str
    options: List[str]
    allow_other: bool


class SessionResponse(BaseModel):
    session_id: str
    summary: str
    selections: List[SelectionResponse]
    should_conclude: bool
    final_output: Optional[dict] = None


class SessionListResponse(BaseModel):
    sessions: List[dict]
    total: int
    limit: int
    offset: int


# Routes
@app.post("/session/start", response_model=SessionResponse)
async def start_session(
    request: StartSessionRequest,
    db: Session = Depends(get_db_session),
):
    """Start a new session with user's raw idea."""
    user_profile_dict = request.user_profile.model_dump() if request.user_profile else None

    logger.info(
        "Starting new session",
        input_length=len(request.input),
        input_preview=request.input[:100] + "..." if len(request.input) > 100 else request.input,
        has_profile=user_profile_dict is not None,
    )

    try:
        orchestrator = Orchestrator()
        output = orchestrator.start_session(request.input, user_profile=user_profile_dict)

        session_id = orchestrator.session.session_id
        orchestrators[session_id] = orchestrator

        # Save to database
        repo = SessionRepository(db)
        repo.create_session(session_id, request.input, user_profile=user_profile_dict)
        repo.add_round(
            session_id=session_id,
            round_number=1,
            agent_output=output.model_dump(),
        )

        logger.info(
            f"Session created: {session_id}",
            session_id=session_id,
            num_questions=len(output.selections),
            should_conclude=output.should_conclude,
        )

        if output.should_conclude:
            logger.info(f"Session {session_id} concluding immediately")
            final = orchestrator.process_selections([])
            if isinstance(final, FinalOutput):
                repo.set_final_output(session_id, final.model_dump())
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
async def submit_selections(
    session_id: str,
    request: SubmitSelectionsRequest,
    db: Session = Depends(get_db_session),
):
    """Submit user selections and get next response."""
    logger.info(
        f"Processing selections for session {session_id}",
        session_id=session_id,
        num_selections=len(request.selections),
    )

    if session_id not in orchestrators:
        logger.warning(f"Session not found in memory: {session_id}")
        raise HTTPException(status_code=404, detail="Session not found or expired")

    orchestrator = orchestrators[session_id]
    repo = SessionRepository(db)

    user_selections = [
        UserSelection(
            question=sel.question,
            selected_option=sel.selected_option,
            custom_input=sel.custom_input,
        )
        for sel in request.selections
    ]

    # Save user selections to current round
    current_round = orchestrator.session.current_round - 1
    repo.update_round_selections(
        session_id=session_id,
        round_number=current_round,
        user_selections=[s.model_dump() for s in user_selections],
    )

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
        # Save final output and cleanup
        repo.set_final_output(session_id, result.model_dump())
        del orchestrators[session_id]

        return SessionResponse(
            session_id=session_id,
            summary="",
            selections=[],
            should_conclude=True,
            final_output=result.model_dump(),
        )

    # Save new round to database
    repo.add_round(
        session_id=session_id,
        round_number=orchestrator.session.current_round - 1,
        agent_output=result.model_dump(),
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


@app.post("/session/{session_id}/end", response_model=SessionResponse)
async def end_session_early(
    session_id: str,
    db: Session = Depends(get_db_session),
):
    """End session early and generate final report."""
    logger.info(f"Early exit requested for session {session_id}", session_id=session_id)

    if session_id not in orchestrators:
        logger.warning(f"Session not found in memory: {session_id}")
        raise HTTPException(status_code=404, detail="Session not found or expired")

    orchestrator = orchestrators[session_id]
    repo = SessionRepository(db)

    try:
        final = orchestrator.force_conclude()

        logger.info(
            f"Session {session_id} ended early",
            session_id=session_id,
            num_action_items=len(final.action_items),
        )

        # Save final output and cleanup
        repo.set_final_output(session_id, final.model_dump())
        del orchestrators[session_id]

        return SessionResponse(
            session_id=session_id,
            summary="",
            selections=[],
            should_conclude=True,
            final_output=final.model_dump(),
        )
    except Exception as e:
        logger.error(f"Failed to end session early: {e}", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/session/{session_id}")
async def get_session(session_id: str, db: Session = Depends(get_db_session)):
    """Get session state from database."""
    logger.debug(f"Getting session state: {session_id}")

    repo = SessionRepository(db)
    session = repo.get_session(session_id)

    if not session:
        logger.warning(f"Session not found: {session_id}")
        raise HTTPException(status_code=404, detail="Session not found")

    return session.to_dict()


@app.get("/sessions", response_model=SessionListResponse)
async def list_sessions(
    status: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db_session),
):
    """List all sessions with optional filtering."""
    logger.debug(f"Listing sessions: status={status}, limit={limit}, offset={offset}")

    repo = SessionRepository(db)
    sessions = repo.get_all_sessions(status=status, limit=limit, offset=offset)
    total = repo.get_session_count(status=status)

    return SessionListResponse(
        sessions=[s.to_dict() for s in sessions],
        total=total,
        limit=limit,
        offset=offset,
    )


@app.delete("/session/{session_id}")
async def delete_session(session_id: str, db: Session = Depends(get_db_session)):
    """Delete a session."""
    logger.info(f"Deleting session: {session_id}")

    repo = SessionRepository(db)
    success = repo.delete_session(session_id)

    if not success:
        raise HTTPException(status_code=404, detail="Session not found")

    # Also remove from memory if present
    if session_id in orchestrators:
        del orchestrators[session_id]

    return {"message": "Session deleted", "session_id": session_id}


# Health check endpoint
@app.get("/health")
async def health_check(db: Session = Depends(get_db_session)):
    """Health check endpoint."""
    repo = SessionRepository(db)
    return {
        "status": "healthy",
        "active_sessions": len(orchestrators),
        "total_sessions": repo.get_session_count(),
        "completed_sessions": repo.get_session_count(status="completed"),
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
    """Initialize database and log startup."""
    init_db()
    logger.info("FastAPI application started")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Log application shutdown."""
    logger.info(f"FastAPI application shutting down. Active sessions: {len(orchestrators)}")
