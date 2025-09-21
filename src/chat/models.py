"""Data models for chat functionality."""

from __future__ import annotations

from typing import TypedDict


class ChatMessage(TypedDict):
    """Represents a single chat message."""

    type: str  # "user" or "assistant"
    content: str


class ChatState(TypedDict):
    """State for chat workflow."""

    messages: list[str]
    chat_history: list[ChatMessage]
    user_input: str | None
    response: str | None
