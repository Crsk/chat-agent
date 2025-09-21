"""Tests for chat models."""

from __future__ import annotations

from src.chat.models import ChatMessage, ChatState


class TestChatMessage:
    """Test ChatMessage TypedDict."""

    def test_chat_message_structure(self) -> None:
        """Test that ChatMessage has correct structure."""
        message: ChatMessage = {"type": "user", "content": "Hello"}

        assert message["type"] == "user"
        assert message["content"] == "Hello"

    def test_chat_message_types(self) -> None:
        """Test different message types."""
        user_message: ChatMessage = {"type": "user", "content": "Question"}
        assistant_message: ChatMessage = {"type": "assistant", "content": "Answer"}

        assert user_message["type"] == "user"
        assert assistant_message["type"] == "assistant"


class TestChatState:
    """Test ChatState TypedDict."""

    def test_chat_state_structure(self) -> None:
        """Test that ChatState has correct structure."""
        state: ChatState = {
            "messages": ["User: Hello", "Assistant: Hi"],
            "chat_history": [
                {"type": "user", "content": "Hello"},
                {"type": "assistant", "content": "Hi"},
            ],
            "user_input": "How are you?",
            "response": "I'm doing well",
        }

        assert len(state["messages"]) == 2
        assert len(state["chat_history"]) == 2
        assert state["user_input"] == "How are you?"
        assert state["response"] == "I'm doing well"

    def test_chat_state_empty(self) -> None:
        """Test empty ChatState."""
        state: ChatState = {
            "messages": [],
            "chat_history": [],
            "user_input": None,
            "response": None,
        }

        assert state["messages"] == []
        assert state["chat_history"] == []
        assert state["user_input"] is None
        assert state["response"] is None

    def test_chat_state_partial(self) -> None:
        """Test ChatState with some None values."""
        state: ChatState = {
            "messages": ["User: Hello"],
            "chat_history": [{"type": "user", "content": "Hello"}],
            "user_input": "Question",
            "response": None,
        }

        assert len(state["messages"]) == 1
        assert state["user_input"] == "Question"
        assert state["response"] is None
