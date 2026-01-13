from typing import Optional

from models import Session, UserSelection, MainAgentOutput, FinalOutput
from agents import MainAgent, Synthesizer
from services.llm_client import LLMClient


class Orchestrator:
    """
    Manages the conversation flow between user and agents.
    Routes to Main Agent or Synthesizer based on conversation state.
    """

    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm_client = llm_client or LLMClient()
        self.main_agent = MainAgent(self.llm_client)
        self.synthesizer = Synthesizer(self.llm_client)
        self.session: Optional[Session] = None

    def start_session(self, user_input: str) -> MainAgentOutput:
        """
        Start a new session with the user's raw idea.

        Args:
            user_input: The user's raw idea/input

        Returns:
            MainAgentOutput from the first round
        """
        self.session = Session(original_input=user_input)

        output = self.main_agent.run(
            original_input=user_input,
            conversation_history=[],
            current_round=1,
        )

        self.session.add_round(output)
        return output

    def process_selections(
        self, selections: list[UserSelection]
    ) -> MainAgentOutput | FinalOutput:
        """
        Process user's selections and get next response.

        Args:
            selections: List of user selections for the current round

        Returns:
            MainAgentOutput if continuing, FinalOutput if concluding
        """
        if not self.session:
            raise ValueError("No active session. Call start_session first.")

        # Add selections to current round
        self.session.add_user_selections(selections)

        # Check if we should conclude based on previous round
        last_round = self.session.conversation_history[-1]
        if last_round.agent_output.should_conclude:
            return self._conclude()

        # Get next round from Main Agent
        output = self.main_agent.run(
            original_input=self.session.original_input,
            conversation_history=self.session.get_history_for_agent(),
            current_round=self.session.current_round,
        )

        self.session.add_round(output)

        # Check if this round should conclude
        if output.should_conclude:
            return self._conclude()

        return output

    def _conclude(self) -> FinalOutput:
        """Generate final output using the Synthesizer."""
        if not self.session:
            raise ValueError("No active session.")

        last_round = self.session.conversation_history[-1]
        final_understanding = last_round.agent_output.understanding

        final_output = self.synthesizer.run(
            original_input=self.session.original_input,
            conversation_history=self.session.get_history_for_agent(),
            final_understanding=final_understanding,
        )

        self.session.complete(final_output)
        return final_output

    def get_session(self) -> Optional[Session]:
        """Get the current session."""
        return self.session
