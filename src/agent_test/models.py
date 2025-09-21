"""Type-safe data models with full typing annotations."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import Any, Protocol, TypeVar

T = TypeVar("T")
U = TypeVar("U")


class Status(Enum):
    """Status enumeration for operations."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(frozen=True)
class Result[T]:
    """Generic result type for operations."""

    value: T
    status: Status
    message: str | None = None

    def is_success(self) -> bool:
        """Check if the result represents a successful operation."""
        return self.status == Status.COMPLETED

    def map(self, func: Callable[[T], U]) -> Result[U]:
        """Transform the result value if successful."""
        if self.is_success():
            return Result(func(self.value), self.status, self.message)
        return Result(None, self.status, self.message)  # type: ignore[arg-type]


class Processor(Protocol[T]):
    """Protocol for processing operations."""

    def process(self, data: T) -> Result[T]:
        """Process data and return a result."""
        ...

    def validate(self, data: T) -> bool:
        """Validate input data."""
        ...


@dataclass
class Config:
    """Configuration with strict typing."""

    name: str
    max_retries: int = 3
    timeout_seconds: float = 30.0
    debug_mode: bool = False
    metadata: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if self.max_retries < 0:
            raise ValueError("max_retries must be non-negative")
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        if not self.name.strip():
            raise ValueError("name cannot be empty")
