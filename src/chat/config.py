"""Configuration management for chat functionality."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

# Load environment variables once at module level
load_dotenv()


@dataclass(frozen=True)
class ChatConfig:
    """Configuration for chat agent."""

    model: str = "openai/gpt-5-mini"
    temperature: float = 0.7
    base_url: str = "https://openrouter.ai/api/v1"
    system_message: str = "You are a helpful assistant. Keep responses concise."

    @property
    def api_key(self) -> str | None:
        """Get API key from environment variables."""
        return os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")

    def validate(self) -> None:
        """Validate configuration."""
        if not self.api_key:
            msg = "OPENROUTER_API_KEY or OPENAI_API_KEY environment variable not set"
            raise ValueError(msg)
