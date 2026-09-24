"""Dynamic cyber state for the AEGIS simulator."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Outcome(str, Enum):
    """Terminal outcomes of a simulation episode."""

    IN_PROGRESS = "in_progress"
    RED_WIN = "red_win"
    BLUE_WIN = "blue_win"
    TIMEOUT = "timeout"


class PrivilegeLevel(str, Enum):
    """Synthetic privilege levels available to Red."""

    NONE = "none"
    USER = "user"
    ADMIN = "admin"


@dataclass
class CyberState:
    """Mutable state describing what is happening during an episode."""

    red_position: str
    discovered_hosts: set[str] = field(default_factory=set)
    compromised_hosts: set[str] = field(default_factory=set)
    detected_hosts: set[str] = field(default_factory=set)
    isolated_hosts: set[str] = field(default_factory=set)
    remediated_vulnerabilities: set[str] = field(default_factory=set)
    host_privileges: dict[str, PrivilegeLevel] = field(default_factory=dict)
    step_count: int = 0
    outcome: Outcome = Outcome.IN_PROGRESS

    def __post_init__(self) -> None:
        if not self.red_position:
            raise ValueError("red_position must not be empty")

        if self.step_count < 0:
            raise ValueError("step_count must not be negative")
