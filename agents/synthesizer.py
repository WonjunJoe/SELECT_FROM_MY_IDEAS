import json

from .base import BaseAgent
from services.llm_client import LLMClient
from models import FinalOutput, Understanding


class Synthesizer(BaseAgent):
    """
    Synthesizer Agent that generates final actionable output.
    Called when the Main Agent decides to conclude the conversation.
    """

    def __init__(self, llm_client: LLMClient):
        super().__init__(llm_client, "synthesizer.txt")

    def run(
        self,
        original_input: str,
        conversation_history: list[dict],
        final_understanding: Understanding,
    ) -> FinalOutput:
        """
        Generate final actionable output from the conversation.

        Args:
            original_input: The user's original raw idea
            conversation_history: Full conversation history
            final_understanding: The Main Agent's final understanding

        Returns:
            FinalOutput with action items, tips, insights, and encouragement
        """
        input_data = {
            "original_input": original_input,
            "conversation_history": conversation_history,
            "final_understanding": final_understanding.model_dump(),
        }

        user_message = json.dumps(input_data, ensure_ascii=False, indent=2)

        response = self.llm_client.chat(
            system_prompt=self.system_prompt,
            user_message=user_message,
            temperature=0.7,
        )

        return FinalOutput.model_validate(response)
