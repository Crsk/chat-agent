"""LLM client abstraction."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Protocol

from langchain.schema import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI  # type: ignore[import-not-found]
from pydantic import SecretStr

from src.chat.config import ChatConfig


class LLMResponse(Protocol):
    """Protocol for LLM response."""

    content: Any


class LLMClient(ABC):
    """Abstract base class for LLM clients."""

    @abstractmethod
    def generate_response(self, user_input: str, system_message: str) -> str:
        """Generate a response to user input."""


class OpenRouterClient(LLMClient):
    """OpenRouter LLM client implementation."""

    def __init__(self, config: ChatConfig) -> None:
        """Initialize the OpenRouter client."""
        config.validate()
        self._config = config
        self._llm = ChatOpenAI(  # type: ignore[misc]
            model=config.model,
            temperature=config.temperature,
            api_key=SecretStr(config.api_key or ""),
            base_url=config.base_url,
        )

    def generate_response(self, user_input: str, system_message: str) -> str:
        """Generate a response using OpenRouter."""
        messages = [
            SystemMessage(content=system_message),
            HumanMessage(content=user_input),
        ]

        response = self._llm.invoke(messages)  # type: ignore[misc]
        return self._extract_content(response)

    def _extract_content(self, response: LLMResponse) -> str:
        """Extract text content from LLM response."""
        content = response.content
        if isinstance(content, str):
            return content
        # Handle list or other types by converting to string
        return str(content) if content else ""
