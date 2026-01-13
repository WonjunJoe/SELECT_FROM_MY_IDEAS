from abc import ABC, abstractmethod
from pathlib import Path

from config import settings
from services.llm_client import LLMClient


class BaseAgent(ABC):
    """Base class for all agents."""

    def __init__(self, llm_client: LLMClient, prompt_file: str):
        self.llm_client = llm_client
        self.system_prompt = self._load_prompt(prompt_file)

    def _load_prompt(self, prompt_file: str) -> str:
        """Load system prompt from file and apply template variables."""
        prompt_path = Path(__file__).parent.parent / "prompts" / prompt_file
        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
        template = prompt_path.read_text(encoding="utf-8")
        return template.format(
            questions_per_round=settings.questions_per_round,
            options_per_question=settings.options_per_question,
            max_rounds=settings.max_rounds,
        )

    @abstractmethod
    def run(self, input_data: dict) -> dict:
        """Run the agent with the given input."""
        pass
