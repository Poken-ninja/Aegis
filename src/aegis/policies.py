"""Baseline policies and observation-derived action candidates."""

from __future__ import annotations

import random
from typing import Protocol

from aegis.actions import Action, ActionType, Agent
from aegis.observations import BlueObservation, RedObservation


class RedPolicy(Protocol):
    """Interface implemented by a Red decision-making policy."""

    def select_action(
        self,
        observation: RedObservation,
        rng: random.Random,
    ) -> Action:
        ...


class BluePolicy(Protocol):
    """Interface implemented by a Blue decision-making policy."""

    def select_action(
        self,
        observation: BlueObservation,
        rng: random.Random,
    ) -> Action:
        ...


def _neighbors(
    connections: frozenset[tuple[str, str]],
    host_id: str,
) -> set[str]:
    neighbors: set[str] = set()

    for source, target in connections:
        if source == host_id:
            neighbors.add(target)
        elif target == host_id:
            neighbors.add(source)

    return neighbors


def red_candidate_actions(observation: RedObservation) -> tuple[Action, ...]:
    """Construct Red action candidates using only the Red observation."""

    neighbors = _neighbors(
        observation.known_connections,
        observation.current_position,
    )

    actions: list[Action] = []

    for target in sorted(neighbors - set(observation.discovered_hosts)):
        actions.append(
            Action(
                agent=Agent.RED,
                action_type=ActionType.DISCOVER,
                target=target,
            )
        )

    if observation.current_position == "internet" or observation.current_host_compromised:
        move_targets = (
            neighbors
            & set(observation.discovered_hosts)
            - set(observation.known_isolated_hosts)
        )
    else:
        move_targets = set()

    for target in sorted(move_targets):
        actions.append(
            Action(
                agent=Agent.RED,
                action_type=ActionType.MOVE,
                target=target,
            )
        )

    if (
        observation.current_position in observation.discovered_hosts
        and observation.known_vulnerabilities
        - observation.known_remediated_vulnerabilities
    ):
        actions.append(
            Action(
                agent=Agent.RED,
                action_type=ActionType.EXPLOIT,
                target=observation.current_position,
            )
        )

    if (
        observation.current_position in observation.discovered_hosts
        and observation.current_host_compromised
        and observation.acquired_privilege != "admin"
        and observation.acquired_privilege != "none"
    ):
        actions.append(
            Action(
                agent=Agent.RED,
                action_type=ActionType.ESCALATE,
                target=observation.current_position,
            )
        )

    return tuple(actions)


def blue_candidate_actions(observation: BlueObservation) -> tuple[Action, ...]:
    """Construct Blue action candidates using only the Blue observation."""

    actions: list[Action] = [
        Action(
            agent=Agent.BLUE,
            action_type=ActionType.MONITOR,
        )
    ]

    telemetry_hosts = {
        endpoint
        for event in observation.telemetry
        for endpoint in (event.source, event.target)
        if endpoint is not None
    }

    for target in sorted(telemetry_hosts):
        actions.append(
            Action(
                agent=Agent.BLUE,
                action_type=ActionType.DETECT,
                target=target,
            )
        )

    for target in sorted(observation.detected_hosts):
        actions.append(
            Action(
                agent=Agent.BLUE,
                action_type=ActionType.ISOLATE,
                target=target,
            )
        )
        actions.append(
            Action(
                agent=Agent.BLUE,
                action_type=ActionType.REMEDIATE,
                target=target,
            )
        )

    return tuple(actions)


class RandomRedPolicy:
    """Random baseline over Red candidates derived from observation."""

    def select_action(
        self,
        observation: RedObservation,
        rng: random.Random,
    ) -> Action:
        candidates = red_candidate_actions(observation)

        if not candidates:
            raise RuntimeError(
                "Red observation produced no candidate actions"
            )

        return rng.choice(candidates)


class RandomBluePolicy:
    """Random baseline over Blue candidates derived from observation."""

    def select_action(
        self,
        observation: BlueObservation,
        rng: random.Random,
    ) -> Action:
        candidates = blue_candidate_actions(observation)

        if not candidates:
            raise RuntimeError(
                "Blue observation produced no candidate actions"
            )

        return rng.choice(candidates)
