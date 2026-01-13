"""
SQLAlchemy database models for session persistence.
"""

from datetime import datetime
from typing import Optional
import json

from sqlalchemy import Column, String, Text, DateTime, Integer, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.ext.hybrid import hybrid_property

Base = declarative_base()


class SessionModel(Base):
    """Database model for user sessions."""

    __tablename__ = "sessions"

    id = Column(String(36), primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    original_input = Column(Text, nullable=False)
    status = Column(String(20), default="in_progress", nullable=False)
    current_round = Column(Integer, default=1, nullable=False)

    # Final output stored as JSON
    _final_output = Column("final_output", Text, nullable=True)

    # Relationships
    rounds = relationship("RoundModel", back_populates="session", cascade="all, delete-orphan", order_by="RoundModel.round_number")

    @hybrid_property
    def final_output(self) -> Optional[dict]:
        """Get final output as dictionary."""
        if self._final_output:
            return json.loads(self._final_output)
        return None

    @final_output.setter
    def final_output(self, value: Optional[dict]):
        """Set final output from dictionary."""
        if value:
            self._final_output = json.dumps(value, ensure_ascii=False)
        else:
            self._final_output = None

    def to_dict(self) -> dict:
        """Convert to dictionary for API response."""
        return {
            "session_id": self.id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "original_input": self.original_input,
            "status": self.status,
            "current_round": self.current_round,
            "final_output": self.final_output,
            "rounds": [r.to_dict() for r in self.rounds],
        }


class RoundModel(Base):
    """Database model for conversation rounds."""

    __tablename__ = "rounds"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(36), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    round_number = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Agent output stored as JSON
    _agent_output = Column("agent_output", Text, nullable=False)

    # User selections stored as JSON
    _user_selections = Column("user_selections", Text, nullable=True)

    # Relationships
    session = relationship("SessionModel", back_populates="rounds")

    @hybrid_property
    def agent_output(self) -> dict:
        """Get agent output as dictionary."""
        return json.loads(self._agent_output)

    @agent_output.setter
    def agent_output(self, value: dict):
        """Set agent output from dictionary."""
        self._agent_output = json.dumps(value, ensure_ascii=False)

    @hybrid_property
    def user_selections(self) -> Optional[list]:
        """Get user selections as list."""
        if self._user_selections:
            return json.loads(self._user_selections)
        return None

    @user_selections.setter
    def user_selections(self, value: Optional[list]):
        """Set user selections from list."""
        if value:
            self._user_selections = json.dumps(value, ensure_ascii=False)
        else:
            self._user_selections = None

    def to_dict(self) -> dict:
        """Convert to dictionary for API response."""
        return {
            "round_number": self.round_number,
            "created_at": self.created_at.isoformat(),
            "agent_output": self.agent_output,
            "user_selections": self.user_selections,
        }
