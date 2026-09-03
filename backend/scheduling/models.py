"""Data models for process scheduling."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

VALID_STATES = frozenset({"NEW", "READY", "RUNNING", "WAITING", "TERMINATED"})


@dataclass
class Process:
    """Represents a process waiting to be scheduled on the CPU."""

    pid: str
    name: str
    arrival_time: int
    burst_time: int
    priority: int = 0
    memory_required: int = 0
    state: str = "NEW"

    def __post_init__(self) -> None:
        if not self.pid:
            raise ValueError("pid cannot be empty")
        if self.arrival_time < 0:
            raise ValueError("arrival_time must be >= 0")
        if self.burst_time <= 0:
            raise ValueError("burst_time must be > 0")
        if self.memory_required < 0:
            raise ValueError("memory_required must be >= 0")
        if self.state not in VALID_STATES:
            raise ValueError(f"invalid state: {self.state}")

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-friendly dictionary representation."""
        return {
            "pid": self.pid,
            "name": self.name,
            "arrival_time": self.arrival_time,
            "burst_time": self.burst_time,
            "priority": self.priority,
            "memory_required": self.memory_required,
            "state": self.state,
        }


@dataclass
class GanttEntry:
    """One segment of the Gantt chart."""

    pid: str | None
    start: int
    end: int

    @property
    def duration(self) -> int:
        return self.end - self.start

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-friendly dictionary representation."""
        return {
            "pid": self.pid,
            "start": self.start,
            "end": self.end,
            "duration": self.duration,
        }


@dataclass
class _ScheduledProcess:
    """Internal process state used during simulation."""

    process: Process
    original_index: int
    remaining_burst: int = field(init=False)
    response_time: int | None = None
    completion_time: int | None = None

    def __post_init__(self) -> None:
        self.remaining_burst = self.process.burst_time
