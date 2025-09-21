"""Tests for LLM client abstraction."""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from src.chat.config import ChatConfig
from src.chat.llm_client import LLMClient, OpenRouterClient


class MockLLMClient(LLMClient):
    """Mock LLM client for testing."""

    def __init__(self, response: str = "Mock response") -> None:
        self.response = response

    def generate_response(self, user_input: str, system_message: str) -> str:
        return f"{self.response} to: {user_input}"


class TestLLMClient:
    """Test LLM client abstract base class."""

    def test_llm_client_abstract(self) -> None:
        """Test that LLMClient cannot be instantiated directly."""
        with pytest.raises(TypeError):
            LLMClient()  # type: ignore[abstract]

    def test_mock_llm_client(self) -> None:
        """Test mock implementation of LLMClient."""
        client = MockLLMClient("Test response")
        result = client.generate_response("Hello", "Be helpful")

        assert result == "Test response to: Hello"


class TestOpenRouterClient:
    """Test OpenRouter LLM client implementation."""

    @patch("src.chat.llm_client.ChatOpenAI")
    @patch.dict("os.environ", {"OPENROUTER_API_KEY": "test_key"})
    def test_openrouter_client_init(self, mock_chat_openai: Mock) -> None:
        """Test OpenRouterClient initialization."""
        config = ChatConfig()
        OpenRouterClient(config)

        mock_chat_openai.assert_called_once()
        call_args = mock_chat_openai.call_args
        assert call_args[1]["model"] == "openai/gpt-5-mini"
        assert call_args[1]["temperature"] == 0.7
        assert call_args[1]["base_url"] == "https://openrouter.ai/api/v1"

    @patch.dict("os.environ", {}, clear=True)
    def test_openrouter_client_validation_error(self) -> None:
        """Test OpenRouterClient with invalid config."""
        config = ChatConfig()

        with pytest.raises(ValueError):
            OpenRouterClient(config)

    @patch("src.chat.llm_client.ChatOpenAI")
    @patch.dict("os.environ", {"OPENROUTER_API_KEY": "test_key"})
    def test_generate_response(self, mock_chat_openai: Mock) -> None:
        """Test response generation."""
        # Setup mocks
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = "Generated response"
        mock_llm.invoke.return_value = mock_response
        mock_chat_openai.return_value = mock_llm

        config = ChatConfig()
        client = OpenRouterClient(config)
        result = client.generate_response("Hello", "Be helpful")

        assert result == "Generated response"
        mock_llm.invoke.assert_called_once()

    @patch("src.chat.llm_client.ChatOpenAI")
    @patch.dict("os.environ", {"OPENROUTER_API_KEY": "test_key"})
    def test_extract_content_string(self, mock_chat_openai: Mock) -> None:
        """Test content extraction with string response."""
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = "String content"
        mock_llm.invoke.return_value = mock_response
        mock_chat_openai.return_value = mock_llm

        config = ChatConfig()
        client = OpenRouterClient(config)
        result = client.generate_response("Test", "System")

        assert result == "String content"

    @patch("src.chat.llm_client.ChatOpenAI")
    @patch.dict("os.environ", {"OPENROUTER_API_KEY": "test_key"})
    def test_extract_content_list(self, mock_chat_openai: Mock) -> None:
        """Test content extraction with list response."""
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = ["item1", "item2"]
        mock_llm.invoke.return_value = mock_response
        mock_chat_openai.return_value = mock_llm

        config = ChatConfig()
        client = OpenRouterClient(config)
        result = client.generate_response("Test", "System")

        assert result == "['item1', 'item2']"

    @patch("src.chat.llm_client.ChatOpenAI")
    @patch.dict("os.environ", {"OPENROUTER_API_KEY": "test_key"})
    def test_extract_content_none(self, mock_chat_openai: Mock) -> None:
        """Test content extraction with None response."""
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = None
        mock_llm.invoke.return_value = mock_response
        mock_chat_openai.return_value = mock_llm

        config = ChatConfig()
        client = OpenRouterClient(config)
        result = client.generate_response("Test", "System")

        assert result == ""
