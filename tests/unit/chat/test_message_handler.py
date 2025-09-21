"""Tests for message handler."""

from __future__ import annotations

from src.chat.config import ChatConfig
from src.chat.llm_client import LLMClient
from src.chat.message_handler import MessageHandler
from src.chat.models import ChatMessage, ChatState


class MockLLMClient(LLMClient):
    """Mock LLM client for testing."""

    def __init__(
        self, response: str = "Mock response", should_raise: bool = False
    ) -> None:
        self.response = response
        self.should_raise = should_raise

    def generate_response(self, user_input: str, system_message: str) -> str:
        if self.should_raise:
            raise RuntimeError("Mock error")
        return self.response


class TestMessageHandler:
    """Test MessageHandler class."""

    def test_init(self) -> None:
        """Test MessageHandler initialization."""
        llm_client = MockLLMClient()
        config = ChatConfig()
        handler = MessageHandler(llm_client, config)

        assert handler._llm_client is llm_client  # type: ignore[reportPrivateUsage]
        assert handler._config is config  # type: ignore[reportPrivateUsage]

    def test_process_message_no_input(self) -> None:
        """Test processing message with no user input."""
        llm_client = MockLLMClient()
        config = ChatConfig()
        handler = MessageHandler(llm_client, config)

        state: ChatState = {
            "messages": [],
            "chat_history": [],
            "user_input": None,
            "response": None,
        }

        result = handler.process_message(state)
        assert result == state

    def test_process_message_empty_input(self) -> None:
        """Test processing message with empty user input."""
        llm_client = MockLLMClient()
        config = ChatConfig()
        handler = MessageHandler(llm_client, config)

        state: ChatState = {
            "messages": [],
            "chat_history": [],
            "user_input": "",
            "response": None,
        }

        result = handler.process_message(state)
        assert result == state

    def test_process_message_success(self) -> None:
        """Test successful message processing."""
        llm_client = MockLLMClient("Generated response")
        config = ChatConfig()
        handler = MessageHandler(llm_client, config)

        state: ChatState = {
            "messages": ["Previous message"],
            "chat_history": [{"type": "user", "content": "Previous"}],
            "user_input": "Hello",
            "response": None,
        }

        result = handler.process_message(state)

        assert len(result["messages"]) == 3
        assert result["messages"][-2] == "User: Hello"
        assert result["messages"][-1] == "Assistant: Generated response"

        assert len(result["chat_history"]) == 3
        assert result["chat_history"][-2] == {"type": "user", "content": "Hello"}
        assert result["chat_history"][-1] == {
            "type": "assistant",
            "content": "Generated response",
        }

        assert result["user_input"] is None
        assert result["response"] == "Generated response"

    def test_process_message_error(self) -> None:
        """Test message processing with LLM error."""
        llm_client = MockLLMClient(should_raise=True)
        config = ChatConfig()
        handler = MessageHandler(llm_client, config)

        state: ChatState = {
            "messages": ["Previous message"],
            "chat_history": [{"type": "user", "content": "Previous"}],
            "user_input": "Hello",
            "response": None,
        }

        result = handler.process_message(state)

        assert len(result["messages"]) == 2
        assert result["messages"][-1] == "Error: Mock error"

        assert result["chat_history"] == state["chat_history"]  # Unchanged
        assert result["user_input"] == "Hello"  # Preserved
        assert result["response"] == "Error: Mock error"

    def test_update_state_success_empty_state(self) -> None:
        """Test successful state update with empty initial state."""
        llm_client = MockLLMClient("Response")
        config = ChatConfig()
        handler = MessageHandler(llm_client, config)

        state: ChatState = {
            "messages": [],
            "chat_history": [],
            "user_input": "Question",
            "response": None,
        }

        result = handler._update_state_success(state, "Question", "Answer")  # type: ignore[reportPrivateUsage]

        assert result["messages"] == ["User: Question", "Assistant: Answer"]
        assert result["chat_history"] == [
            {"type": "user", "content": "Question"},
            {"type": "assistant", "content": "Answer"},
        ]
        assert result["user_input"] is None
        assert result["response"] == "Answer"

    def test_update_state_error_preserves_state(self) -> None:
        """Test error state update preserves original state."""
        llm_client = MockLLMClient()
        config = ChatConfig()
        handler = MessageHandler(llm_client, config)

        original_history: list[ChatMessage] = [{"type": "user", "content": "Previous"}]
        state: ChatState = {
            "messages": ["Previous"],
            "chat_history": original_history,
            "user_input": "Current",
            "response": None,
        }

        result = handler._update_state_error(state, "Test error")  # type: ignore[reportPrivateUsage]

        assert result["messages"] == ["Previous", "Error: Test error"]
        assert result["chat_history"] is original_history  # Same reference
        assert result["user_input"] == "Current"
        assert result["response"] == "Error: Test error"

    def test_state_immutability(self) -> None:
        """Test that original state is not mutated."""
        llm_client = MockLLMClient("Response")
        config = ChatConfig()
        handler = MessageHandler(llm_client, config)

        original_messages = ["Original"]
        original_history: list[ChatMessage] = [{"type": "user", "content": "Original"}]
        state: ChatState = {
            "messages": original_messages,
            "chat_history": original_history,
            "user_input": "Test",
            "response": None,
        }

        result = handler.process_message(state)

        # Original state should be unchanged
        assert state["messages"] == ["Original"]
        assert state["chat_history"] == [{"type": "user", "content": "Original"}]

        # Result should have new data
        assert len(result["messages"]) == 3
        assert len(result["chat_history"]) == 3
