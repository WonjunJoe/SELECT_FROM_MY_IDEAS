from abc import ABC, abstractmethod
from pathlib import Path

from services.llm_client import LLMClient


class BaseAgent(ABC):
    """Base class for all agents."""

    def __init__(self, llm_client: LLMClient, prompt_file: str):
        self.llm_client = llm_client
        self.system_prompt = self._load_prompt(prompt_file)

    def _load_prompt(self, prompt_file: str) -> str:
        """Load system prompt from file."""
        prompt_path = Path(__file__).parent.parent / "prompts" / prompt_file
        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
        return prompt_path.read_text(encoding="utf-8")

    @abstractmethod
    def run(self, input_data: dict) -> dict:
        """Run the agent with the given input."""
        pass
