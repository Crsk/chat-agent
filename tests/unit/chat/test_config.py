"""Tests for chat configuration."""

from __future__ import annotations

import os
from unittest.mock import patch

import pytest

from src.chat.config import ChatConfig


class TestChatConfig:
    """Test ChatConfig class."""

    def test_default_config(self) -> None:
        """Test default configuration values."""
        config = ChatConfig()

        assert config.model == "openai/gpt-5-mini"
        assert config.temperature == 0.7
        assert config.base_url == "https://openrouter.ai/api/v1"
        assert (
            config.system_message
            == "You are a helpful assistant. Keep responses concise."
        )

    def test_custom_config(self) -> None:
        """Test custom configuration values."""
        config = ChatConfig(
            model="custom/model",
            temperature=0.5,
            base_url="https://custom.api/v1",
            system_message="Custom system message",
        )

        assert config.model == "custom/model"
        assert config.temperature == 0.5
        assert config.base_url == "https://custom.api/v1"
        assert config.system_message == "Custom system message"

    def test_config_immutable(self) -> None:
        """Test that config is immutable (frozen dataclass)."""
        config = ChatConfig()

        with pytest.raises(AttributeError):
            config.model = "new/model"  # type: ignore[misc]

    @patch.dict(os.environ, {"OPENROUTER_API_KEY": "test_openrouter_key"})
    def test_api_key_openrouter(self) -> None:
        """Test API key retrieval with OPENROUTER_API_KEY."""
        config = ChatConfig()
        assert config.api_key == "test_openrouter_key"

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test_openai_key"}, clear=True)
    def test_api_key_openai_fallback(self) -> None:
        """Test API key fallback to OPENAI_API_KEY."""
        config = ChatConfig()
        assert config.api_key == "test_openai_key"

    @patch.dict(
        os.environ,
        {"OPENROUTER_API_KEY": "openrouter_key", "OPENAI_API_KEY": "openai_key"},
    )
    def test_api_key_priority(self) -> None:
        """Test that OPENROUTER_API_KEY takes priority."""
        config = ChatConfig()
        assert config.api_key == "openrouter_key"

    @patch.dict(os.environ, {}, clear=True)
    def test_api_key_none(self) -> None:
        """Test API key when no environment variables are set."""
        config = ChatConfig()
        assert config.api_key is None

    @patch.dict(os.environ, {"OPENROUTER_API_KEY": "valid_key"})
    def test_validate_success(self) -> None:
        """Test successful validation with API key."""
        config = ChatConfig()
        config.validate()  # Should not raise

    @patch.dict(os.environ, {}, clear=True)
    def test_validate_failure(self) -> None:
        """Test validation failure without API key."""
        config = ChatConfig()

        with pytest.raises(ValueError, match="OPENROUTER_API_KEY or OPENAI_API_KEY"):
            config.validate()
