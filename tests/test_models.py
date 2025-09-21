"""Tests for models module with full type safety."""

import pytest

from agent_test.models import Config, Result, Status


def test_result_creation() -> None:
    """Test Result creation and basic functionality."""
    result: Result[str] = Result("success", Status.COMPLETED, "All good")

    assert result.value == "success"
    assert result.status == Status.COMPLETED
    assert result.message == "All good"
    assert result.is_success() is True


def test_result_failure() -> None:
    """Test Result with failure status."""
    result: Result[int] = Result(0, Status.FAILED, "Error occurred")

    assert result.value == 0
    assert result.status == Status.FAILED
    assert result.is_success() is False


def test_result_map_success() -> None:
    """Test Result.map with successful result."""
    result: Result[int] = Result(5, Status.COMPLETED)
    mapped: Result[str] = result.map(str)

    assert mapped.value == "5"
    assert mapped.status == Status.COMPLETED


def test_config_creation() -> None:
    """Test Config creation with defaults."""
    config = Config("test-config")

    assert config.name == "test-config"
    assert config.max_retries == 3
    assert config.timeout_seconds == 30.0
    assert config.debug_mode is False
    assert config.metadata is None


def test_config_validation() -> None:
    """Test Config validation in __post_init__."""
    with pytest.raises(ValueError, match="max_retries must be non-negative"):
        Config("test", max_retries=-1)

    with pytest.raises(ValueError, match="timeout_seconds must be positive"):
        Config("test", timeout_seconds=0)

    with pytest.raises(ValueError, match="name cannot be empty"):
        Config("   ")
