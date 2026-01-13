from typing import Optional, Literal
from datetime import datetime
from pydantic import BaseModel, Field
import uuid

from .agent_io import MainAgentOutput, FinalOutput


class UserSelection(BaseModel):
    """Represents a user's selection for a question."""

    question: str = Field(description="The question that was asked")
    selected_option: Optional[str] = Field(
        default=None, description="The option selected by the user"
    )
    custom_input: Optional[str] = Field(
        default=None, description="Custom input if 'Other' was selected"
    )


class Round(BaseModel):
    """Represents a single round of conversation."""

    round_number: int = Field(description="The round number (1-indexed)")
    agent_output: MainAgentOutput = Field(description="Output from the Main Agent")
    user_selections: list[UserSelection] = Field(
        default_factory=list, description="User's selections for this round"
    )


class Session(BaseModel):
    """Represents an entire conversation session."""

    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.now)
    original_input: str = Field(description="The user's original raw input")
    conversation_history: list[Round] = Field(
        default_factory=list, description="History of all rounds"
    )
    current_round: int = Field(default=1, description="Current round number")
    status: Literal["in_progress", "completed"] = Field(default="in_progress")
    final_output: Optional[FinalOutput] = Field(
        default=None, description="Final output if session is completed"
    )

    def add_round(self, agent_output: MainAgentOutput) -> Round:
        """Add a new round with agent output."""
        round_obj = Round(
            round_number=self.current_round,
            agent_output=agent_output,
            user_selections=[],
        )
        self.conversation_history.append(round_obj)
        return round_obj

    def add_user_selections(self, selections: list[UserSelection]) -> None:
        """Add user selections to the current round."""
        if self.conversation_history:
            self.conversation_history[-1].user_selections = selections
            self.current_round += 1

    def get_history_for_agent(self) -> list[dict]:
        """Get conversation history formatted for agent input."""
        history = []
        for round_obj in self.conversation_history:
            history.append(
                {
                    "round": round_obj.round_number,
                    "summary": round_obj.agent_output.summary,
                    "questions": [
                        {"question": s.question, "options": s.options}
                        for s in round_obj.agent_output.selections
                    ],
                    "user_selections": [
                        {
                            "question": sel.question,
                            "selected": sel.selected_option or sel.custom_input,
                        }
                        for sel in round_obj.user_selections
                    ],
                }
            )
        return history

    def complete(self, final_output: FinalOutput) -> None:
        """Mark the session as completed with final output."""
        self.status = "completed"
        self.final_output = final_output
