"""Action definitions for the AEGIS simulator."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Agent(str, Enum):
    """Agents that can act in an AEGIS episode."""

    RED = "red"
    BLUE = "blue"


class ActionType(str, Enum):
    """Abstract cybersecurity actions available to the agents."""

    DISCOVER = "discover"
    EXPLOIT = "exploit"
    MOVE = "move"
    ESCALATE = "escalate"

    MONITOR = "monitor"
    DETECT = "detect"
    ISOLATE = "isolate"
    REMEDIATE = "remediate"


@dataclass(frozen=True)
class Action:
    """An agent action and its optional simulation target."""

    agent: Agent
    action_type: ActionType
    target: str | None = None