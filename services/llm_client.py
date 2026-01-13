import os
import json
from typing import Optional

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class LLMClient:
    """Wrapper for OpenAI API with JSON mode support."""

    def __init__(self, model: str = "gpt-4o"):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY not found. Please set it in your .env file."
            )
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def chat(
        self,
        system_prompt: str,
        user_message: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> dict:
        """
        Send a chat completion request and return parsed JSON response.

        Args:
            system_prompt: The system prompt for the assistant
            user_message: The user's message
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens in response

        Returns:
            Parsed JSON response as a dictionary
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]

        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "response_format": {"type": "json_object"},
        }

        if max_tokens:
            kwargs["max_tokens"] = max_tokens

        response = self.client.chat.completions.create(**kwargs)
        content = response.choices[0].message.content

        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON response: {e}\nContent: {content}")

    def chat_with_history(
        self,
        system_prompt: str,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> dict:
        """
        Send a chat completion request with message history.

        Args:
            system_prompt: The system prompt for the assistant
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens in response

        Returns:
            Parsed JSON response as a dictionary
        """
        full_messages = [{"role": "system", "content": system_prompt}] + messages

        kwargs = {
            "model": self.model,
            "messages": full_messages,
            "temperature": temperature,
            "response_format": {"type": "json_object"},
        }

        if max_tokens:
            kwargs["max_tokens"] = max_tokens

        response = self.client.chat.completions.create(**kwargs)
        content = response.choices[0].message.content

        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON response: {e}\nContent: {content}")
