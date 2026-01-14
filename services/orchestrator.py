from typing import Optional

from models import Session, UserSelection, MainAgentOutput, FinalOutput
from agents import MainAgent, Synthesizer
from services.llm_client import LLMClient
from core.logging import logger


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
        logger.debug("Orchestrator initialized")

    def start_session(
        self, user_input: str, user_profile: Optional[dict] = None
    ) -> MainAgentOutput:
        """
        Start a new session with the user's raw idea.

        Args:
            user_input: The user's raw idea/input
            user_profile: Optional user profile for personalization

        Returns:
            MainAgentOutput from the first round
        """
        self.session = Session(original_input=user_input, user_profile=user_profile)
        logger.info(
            f"Session started: {self.session.session_id}",
            session_id=self.session.session_id,
            input_length=len(user_input),
            has_profile=user_profile is not None,
        )

        output = self.main_agent.run(
            original_input=user_input,
            conversation_history=[],
            current_round=1,
            user_profile=user_profile,
        )

        self.session.add_round(output)
        logger.debug(
            f"First round completed for session {self.session.session_id}",
            num_selections=len(output.selections),
            should_conclude=output.should_conclude,
        )
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
            logger.error("No active session when processing selections")
            raise ValueError("No active session. Call start_session first.")

        logger.debug(
            f"Processing {len(selections)} selections for session {self.session.session_id}",
            session_id=self.session.session_id,
            num_selections=len(selections),
        )

        # Add selections to current round
        self.session.add_user_selections(selections)

        # Check if we should conclude based on previous round
        last_round = self.session.conversation_history[-1]
        if last_round.agent_output.should_conclude:
            logger.info(f"Session {self.session.session_id} concluding based on last round")
            return self._conclude()

        # Get next round from Main Agent
        logger.debug(f"Getting next round from Main Agent (round {self.session.current_round})")
        output = self.main_agent.run(
            original_input=self.session.original_input,
            conversation_history=self.session.get_history_for_agent(),
            current_round=self.session.current_round,
            user_profile=self.session.user_profile,
        )

        self.session.add_round(output)

        logger.debug(
            f"Round {self.session.current_round - 1} completed",
            session_id=self.session.session_id,
            num_selections=len(output.selections),
            should_conclude=output.should_conclude,
        )

        # Check if this round should conclude
        if output.should_conclude:
            logger.info(f"Session {self.session.session_id} concluding after round {self.session.current_round - 1}")
            return self._conclude()

        return output

    def _conclude(self) -> FinalOutput:
        """Generate final output using the Synthesizer."""
        if not self.session:
            logger.error("No active session when concluding")
            raise ValueError("No active session.")

        logger.info(
            f"Synthesizing final output for session {self.session.session_id}",
            session_id=self.session.session_id,
            total_rounds=len(self.session.conversation_history),
        )

        last_round = self.session.conversation_history[-1]
        final_understanding = last_round.agent_output.understanding

        final_output = self.synthesizer.run(
            original_input=self.session.original_input,
            conversation_history=self.session.get_history_for_agent(),
            final_understanding=final_understanding,
            user_profile=self.session.user_profile,
        )

        self.session.complete(final_output)

        logger.info(
            f"Session {self.session.session_id} completed",
            session_id=self.session.session_id,
            num_action_items=len(final_output.action_items),
            num_tips=len(final_output.tips),
            num_insights=len(final_output.insights),
        )

        return final_output

    def force_conclude(self) -> FinalOutput:
        """
        Force early conclusion of the session.
        Generates final report even if agent hasn't decided to conclude.

        Returns:
            FinalOutput with summary and action items based on current progress
        """
        if not self.session:
            logger.error("No active session when forcing conclusion")
            raise ValueError("No active session. Call start_session first.")

        logger.info(
            f"Force concluding session {self.session.session_id}",
            session_id=self.session.session_id,
            current_round=self.session.current_round,
        )

        return self._conclude()

    def get_session(self) -> Optional[Session]:
        """Get the current session."""
        return self.session
