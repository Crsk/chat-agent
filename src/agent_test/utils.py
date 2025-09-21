"""Utility functions with comprehensive type annotations."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Awaitable, Callable, Iterable, Sequence
from contextlib import asynccontextmanager
from typing import Any, ParamSpec, TypeVar, overload

from .models import Config, Result, Status

P = ParamSpec("P")
T = TypeVar("T")
U = TypeVar("U")


def safe_divide(numerator: float, denominator: float) -> Result[float]:
    """Safely divide two numbers with proper error handling."""
    if denominator == 0:
        return Result(0.0, Status.FAILED, "Division by zero")

    result = numerator / denominator
    return Result(result, Status.COMPLETED, "Division successful")


@overload
def get_first[T](items: Sequence[T]) -> T | None: ...


@overload
def get_first[T, U](items: Sequence[T], default: U) -> T | U: ...


def get_first[T](items: Sequence[T], default: Any = None) -> T | Any:
    """Get the first item from a sequence with optional default."""
    return items[0] if items else default


def retry_async(
    max_attempts: int = 3,
) -> Callable[[Callable[P, Awaitable[T]]], Callable[P, Awaitable[T]]]:
    """Decorator for retrying async functions with exponential backoff."""

    def decorator(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            last_exception: Exception | None = None

            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        await asyncio.sleep(2**attempt)

            if last_exception:
                raise last_exception
            raise RuntimeError("Retry failed without exception")

        return wrapper

    return decorator


@asynccontextmanager
async def managed_resource(config: Config) -> AsyncIterator[dict[str, Any]]:
    """Context manager for managing resources with proper cleanup."""
    resource: dict[str, Any] = {
        "name": config.name,
        "created_at": asyncio.get_event_loop().time(),
        "active": True,
    }

    try:
        yield resource
    finally:
        resource["active"] = False


def process_items(
    items: Iterable[T],
    processor: Callable[[T], U],
    *,
    filter_func: Callable[[T], bool] | None = None,
) -> list[U]:
    """Process items with optional filtering."""
    if filter_func is None:

        def _default_filter(_: T) -> bool:
            return True

        filter_func = _default_filter

    return [processor(item) for item in items if filter_func(item)]


class TypedCache[T]:
    """Type-safe cache implementation."""

    def __init__(self, max_size: int = 100) -> None:
        self._cache: dict[str, T] = {}
        self._max_size = max_size

    def get(self, key: str) -> T | None:
        """Get value from cache."""
        return self._cache.get(key)

    def set(self, key: str, value: T) -> None:
        """Set value in cache with size management."""
        if len(self._cache) >= self._max_size and key not in self._cache:
            # Remove oldest item (simplified LRU)
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]

        self._cache[key] = value

    def clear(self) -> None:
        """Clear all cached items."""
        self._cache.clear()
