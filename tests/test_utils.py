"""Tests for utils module with comprehensive typing."""

from agent_test.models import Status
from agent_test.utils import TypedCache, get_first, process_items, safe_divide


def test_safe_divide_success() -> None:
    """Test successful division."""
    result = safe_divide(10.0, 2.0)

    assert result.value == 5.0
    assert result.status == Status.COMPLETED
    assert result.message == "Division successful"


def test_safe_divide_by_zero() -> None:
    """Test division by zero handling."""
    result = safe_divide(10.0, 0.0)

    assert result.value == 0.0
    assert result.status == Status.FAILED
    assert result.message == "Division by zero"


def test_get_first_with_items() -> None:
    """Test get_first with non-empty sequence."""
    items = [1, 2, 3, 4]
    first = get_first(items)

    assert first == 1


def test_get_first_empty_no_default() -> None:
    """Test get_first with empty sequence and no default."""
    items: list[int] = []
    first = get_first(items)

    assert first is None


def test_get_first_empty_with_default() -> None:
    """Test get_first with empty sequence and default value."""
    items: list[str] = []
    first = get_first(items, "default")

    assert first == "default"


def test_process_items_no_filter() -> None:
    """Test process_items without filtering."""
    items = [1, 2, 3, 4]
    result = process_items(items, lambda x: x * 2)

    assert result == [2, 4, 6, 8]


def test_process_items_with_filter() -> None:
    """Test process_items with filtering."""
    items = [1, 2, 3, 4, 5]
    result = process_items(
        items,
        lambda x: x * 2,
        filter_func=lambda x: x % 2 == 0,
    )

    assert result == [4, 8]


def test_typed_cache() -> None:
    """Test TypedCache functionality."""
    cache: TypedCache[str] = TypedCache(max_size=2)

    # Test setting and getting
    cache.set("key1", "value1")
    assert cache.get("key1") == "value1"

    # Test missing key
    assert cache.get("missing") is None

    # Test size limit
    cache.set("key2", "value2")
    cache.set("key3", "value3")  # Should evict key1

    assert cache.get("key1") is None
    assert cache.get("key2") == "value2"
    assert cache.get("key3") == "value3"

    # Test clear
    cache.clear()
    assert cache.get("key2") is None
    assert cache.get("key3") is None
