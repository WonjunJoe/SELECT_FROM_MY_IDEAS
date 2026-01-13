from typing import Optional, Literal
from pydantic import BaseModel, Field


class Understanding(BaseModel):
    """Represents the agent's understanding of the user's idea."""

    main_themes: list[str] = Field(description="Main themes identified from the input")
    user_intent: str = Field(description="The user's underlying intent or goal")
    clarified_points: list[str] = Field(description="Points that have been clarified")
    remaining_uncertainties: list[str] = Field(
        description="Points that still need clarification"
    )


class Selection(BaseModel):
    """A question with multiple choice options for the user."""

    question: str = Field(description="The question to ask the user")
    options: list[str] = Field(description="Available options to choose from")
    allow_other: bool = Field(
        default=True, description="Whether to allow custom input"
    )


class MainAgentOutput(BaseModel):
    """Output from the Main Agent."""

    understanding: Understanding = Field(
        description="Current understanding of the user's idea"
    )
    summary: str = Field(description="Summary of the conversation so far")
    selections: list[Selection] = Field(
        description="Questions and options for the user"
    )
    should_conclude: bool = Field(
        description="Whether to conclude the conversation and generate final output"
    )
    conclusion_reason: Optional[str] = Field(
        default=None, description="Reason for concluding (if should_conclude is True)"
    )


class ActionItem(BaseModel):
    """A specific action item for the user."""

    action: str = Field(description="The specific action to take")
    priority: Literal["high", "medium", "low"] = Field(description="Priority level")
    effort: Literal["minimal", "moderate", "significant"] = Field(
        description="Estimated effort required"
    )


class FinalOutput(BaseModel):
    """Final synthesized output for the user."""

    final_summary: str = Field(description="Summary of the entire conversation")
    action_items: list[ActionItem] = Field(description="Concrete action items")
    tips: list[str] = Field(description="Practical tips for the user")
    insights: list[str] = Field(description="Personalized insights")
    next_steps: str = Field(description="Recommended next steps")
    encouragement: str = Field(description="Encouraging message for the user")
