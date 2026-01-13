import os
import json
import time
from typing import Optional

from openai import OpenAI
from dotenv import load_dotenv

from core.logging import logger

load_dotenv()


class LLMClient:
    """Wrapper for OpenAI API with JSON mode support."""

    def __init__(self, model: str = "gpt-4o"):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.error("OPENAI_API_KEY not found in environment")
            raise ValueError(
                "OPENAI_API_KEY not found. Please set it in your .env file."
            )
        self.client = OpenAI(api_key=api_key)
        self.model = model
        logger.info(f"LLMClient initialized with model: {model}")

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

        start_time = time.time()
        logger.debug(
            "LLM chat request",
            model=self.model,
            temperature=temperature,
            user_message_length=len(user_message),
        )

        try:
            response = self.client.chat.completions.create(**kwargs)
            elapsed = time.time() - start_time

            content = response.choices[0].message.content
            usage = response.usage

            logger.info(
                "LLM chat response received",
                model=self.model,
                elapsed_ms=round(elapsed * 1000, 2),
                prompt_tokens=usage.prompt_tokens if usage else None,
                completion_tokens=usage.completion_tokens if usage else None,
                total_tokens=usage.total_tokens if usage else None,
            )

            try:
                return json.loads(content)
            except json.JSONDecodeError as e:
                logger.error(
                    f"Failed to parse JSON response: {e}",
                    content_preview=content[:200] if content else None,
                )
                raise ValueError(f"Failed to parse JSON response: {e}\nContent: {content}")

        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(
                f"LLM chat request failed: {e}",
                model=self.model,
                elapsed_ms=round(elapsed * 1000, 2),
                error=str(e),
            )
            raise

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

        start_time = time.time()
        logger.debug(
            "LLM chat_with_history request",
            model=self.model,
            temperature=temperature,
            num_messages=len(messages),
        )

        try:
            response = self.client.chat.completions.create(**kwargs)
            elapsed = time.time() - start_time

            content = response.choices[0].message.content
            usage = response.usage

            logger.info(
                "LLM chat_with_history response received",
                model=self.model,
                elapsed_ms=round(elapsed * 1000, 2),
                prompt_tokens=usage.prompt_tokens if usage else None,
                completion_tokens=usage.completion_tokens if usage else None,
                total_tokens=usage.total_tokens if usage else None,
            )

            try:
                return json.loads(content)
            except json.JSONDecodeError as e:
                logger.error(
                    f"Failed to parse JSON response: {e}",
                    content_preview=content[:200] if content else None,
                )
                raise ValueError(f"Failed to parse JSON response: {e}\nContent: {content}")

        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(
                f"LLM chat_with_history request failed: {e}",
                model=self.model,
                elapsed_ms=round(elapsed * 1000, 2),
                error=str(e),
            )
            raise
