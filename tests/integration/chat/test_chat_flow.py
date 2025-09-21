"""Integration tests for complete chat workflow."""

from __future__ import annotations

import os
from typing import Any
from unittest.mock import Mock, patch

import pytest

from src.chat.config import ChatConfig
from src.chat.models import ChatState
from src.chat.workflow import create_chat_agent


class TestChatIntegration:
    """Integration tests for chat components working together."""

    @patch.dict(os.environ, {"OPENROUTER_API_KEY": "test_key"})
    @patch("src.chat.llm_client.ChatOpenAI")
    def test_complete_chat_workflow(self, mock_chat_openai: Mock) -> None:
        """Test complete chat workflow from input to response."""
        # Setup mock LLM response
        mock_llm = mock_chat_openai.return_value
        mock_response = type(
            "MockResponse", (), {"content": "Hello! How can I help you?"}
        )()
        mock_llm.invoke.return_value = mock_response

        # Create agent with real configuration
        config = ChatConfig(model="test/model", temperature=0.5)
        agent = create_chat_agent(config)

        # Test initial state
        initial_state: ChatState = {
            "messages": [],
            "chat_history": [],
            "user_input": "Hello",
            "response": None,
        }

        # Process through workflow
        result = agent.invoke(initial_state)

        # Verify complete integration
        assert result["response"] == "Hello! How can I help you?"
        assert len(result["messages"]) == 2
        assert result["messages"][0] == "User: Hello"
        assert result["messages"][1] == "Assistant: Hello! How can I help you?"

        assert len(result["chat_history"]) == 2
        assert result["chat_history"][0]["type"] == "user"
        assert result["chat_history"][0]["content"] == "Hello"
        assert result["chat_history"][1]["type"] == "assistant"
        assert result["chat_history"][1]["content"] == "Hello! How can I help you?"

        # Verify LLM was called with correct parameters
        mock_chat_openai.assert_called_once()
        call_kwargs: dict[str, Any] = mock_chat_openai.call_args[1]  # type: ignore[assignment]
        assert call_kwargs["model"] == "test/model"
        assert call_kwargs["temperature"] == 0.5

    @patch.dict(os.environ, {"OPENROUTER_API_KEY": "test_key"})
    @patch("src.chat.llm_client.ChatOpenAI")
    def test_multi_turn_conversation(self, mock_chat_openai: Mock) -> None:
        """Test multi-turn conversation maintaining state."""
        # Setup mock responses
        mock_llm = mock_chat_openai.return_value
        responses = [
            type("MockResponse", (), {"content": "Hello! I'm Claude."})(),
            type("MockResponse", (), {"content": "I can help with many tasks."})(),
        ]
        mock_llm.invoke.side_effect = responses

        # Create agent
        agent = create_chat_agent()

        # First exchange
        state1: ChatState = {
            "messages": [],
            "chat_history": [],
            "user_input": "Hi there",
            "response": None,
        }
        result1 = agent.invoke(state1)

        # Second exchange using previous state
        state2: ChatState = {
            "messages": result1["messages"],
            "chat_history": result1["chat_history"],
            "user_input": "What can you do?",
            "response": None,
        }
        result2 = agent.invoke(state2)

        # Verify conversation continuity
        assert len(result2["messages"]) == 4
        assert len(result2["chat_history"]) == 4

        # Check conversation flow
        expected_messages = [
            "User: Hi there",
            "Assistant: Hello! I'm Claude.",
            "User: What can you do?",
            "Assistant: I can help with many tasks.",
        ]
        assert result2["messages"] == expected_messages

    @patch.dict(os.environ, {}, clear=True)
    def test_config_validation_integration(self) -> None:
        """Test that configuration validation works in real workflow."""
        with pytest.raises(ValueError, match="OPENROUTER_API_KEY or OPENAI_API_KEY"):
            create_chat_agent()

    # Error handling is thoroughly tested in unit tests
