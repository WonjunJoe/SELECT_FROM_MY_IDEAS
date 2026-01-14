"""
Repository pattern for session data access.
"""

from typing import Optional, List
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from .models import SessionModel, RoundModel
from core.logging import logger


class SessionRepository:
    """Repository for session CRUD operations."""

    def __init__(self, db: Session):
        self.db = db

    def create_session(
        self,
        session_id: str,
        original_input: str,
        user_profile: Optional[dict] = None,
    ) -> SessionModel:
        """Create a new session."""
        logger.debug(f"Creating session: {session_id}", has_profile=user_profile is not None)

        session = SessionModel(
            id=session_id,
            original_input=original_input,
            status="in_progress",
            current_round=1,
        )
        session.user_profile = user_profile
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)

        logger.info(f"Session created: {session_id}")
        return session

    def get_session(self, session_id: str) -> Optional[SessionModel]:
        """Get session by ID."""
        return self.db.query(SessionModel).filter(SessionModel.id == session_id).first()

    def get_all_sessions(
        self,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[SessionModel]:
        """Get all sessions with optional filtering."""
        query = self.db.query(SessionModel)

        if status:
            query = query.filter(SessionModel.status == status)

        return (
            query.order_by(SessionModel.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    def update_session_status(self, session_id: str, status: str) -> Optional[SessionModel]:
        """Update session status."""
        session = self.get_session(session_id)
        if session:
            session.status = status
            session.updated_at = datetime.now(timezone.utc)
            self.db.commit()
            logger.info(f"Session {session_id} status updated to {status}")
        return session

    def update_session_round(self, session_id: str, round_number: int) -> Optional[SessionModel]:
        """Update current round number."""
        session = self.get_session(session_id)
        if session:
            session.current_round = round_number
            session.updated_at = datetime.now(timezone.utc)
            self.db.commit()
        return session

    def set_final_output(self, session_id: str, final_output: dict) -> Optional[SessionModel]:
        """Set final output and mark session as completed."""
        session = self.get_session(session_id)
        if session:
            session.final_output = final_output
            session.status = "completed"
            session.updated_at = datetime.now(timezone.utc)
            self.db.commit()
            logger.info(f"Session {session_id} completed with final output")
        return session

    def add_round(
        self,
        session_id: str,
        round_number: int,
        agent_output: dict,
    ) -> Optional[RoundModel]:
        """Add a new round to session."""
        session = self.get_session(session_id)
        if not session:
            logger.warning(f"Session not found: {session_id}")
            return None

        round_model = RoundModel(
            session_id=session_id,
            round_number=round_number,
            _agent_output="{}",  # Will be set properly below
        )
        round_model.agent_output = agent_output

        self.db.add(round_model)
        session.current_round = round_number + 1
        session.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(round_model)

        logger.debug(f"Round {round_number} added to session {session_id}")
        return round_model

    def update_round_selections(
        self,
        session_id: str,
        round_number: int,
        user_selections: list,
    ) -> Optional[RoundModel]:
        """Update user selections for a round."""
        round_model = (
            self.db.query(RoundModel)
            .filter(
                RoundModel.session_id == session_id,
                RoundModel.round_number == round_number,
            )
            .first()
        )

        if round_model:
            round_model.user_selections = user_selections
            self.db.commit()
            logger.debug(f"Round {round_number} selections updated for session {session_id}")

        return round_model

    def delete_session(self, session_id: str) -> bool:
        """Delete a session and all related data."""
        session = self.get_session(session_id)
        if session:
            self.db.delete(session)
            self.db.commit()
            logger.info(f"Session deleted: {session_id}")
            return True
        return False

    def get_session_count(self, status: Optional[str] = None) -> int:
        """Get count of sessions."""
        query = self.db.query(SessionModel)
        if status:
            query = query.filter(SessionModel.status == status)
        return query.count()
