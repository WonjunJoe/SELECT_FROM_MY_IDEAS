import json
from typing import Optional

from .base import BaseAgent
from services.llm_client import LLMClient
from models import MainAgentOutput


class MainAgent(BaseAgent):
    """
    Main Agent that handles conversation logic:
    - Extracts key information from raw input
    - Generates clarifying questions with options
    - Tracks conversation context
    - Decides when to conclude
    """

    def __init__(self, llm_client: LLMClient):
        super().__init__(llm_client, "main_agent.txt")

    def run(
        self,
        original_input: str,
        conversation_history: list[dict],
        current_round: int,
        user_profile: Optional[dict] = None,
    ) -> MainAgentOutput:
        """
        Process input and generate questions/options or decide to conclude.

        Args:
            original_input: The user's original raw idea
            conversation_history: List of previous rounds
            current_round: Current round number
            user_profile: Optional user profile for personalization

        Returns:
            MainAgentOutput with understanding, summary, selections, and conclusion decision
        """
        input_data = {
            "user_profile": user_profile,
            "original_input": original_input,
            "conversation_history": conversation_history,
            "current_round": current_round,
        }

        user_message = json.dumps(input_data, ensure_ascii=False, indent=2)

        response = self.llm_client.chat(
            system_prompt=self.system_prompt,
            user_message=user_message,
            temperature=0.7,
        )

        return MainAgentOutput.model_validate(response)
