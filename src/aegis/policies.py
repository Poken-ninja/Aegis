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


class HeuristicRedPolicy:
    """Deterministic Red baseline using only the public Red observation.

    Priority:
    1. Escalate an available foothold.
    2. Exploit the current host when a vulnerability is known.
    3. Discover an unknown neighbor.
    4. Move toward the highest-priority known host role.

    This is a hand-written baseline, not a learned policy.
    """

    _ROLE_PRIORITY = {
        "critical_asset": 0,
        "database_server": 1,
        "application_server": 2,
        "workstation": 3,
        "web_server": 4,
        "external_entry": 5,
    }

    def select_action(
        self,
        observation: RedObservation,
        rng: random.Random,
    ) -> Action:
        candidates = red_candidate_actions(observation)

        escalations = [
            action
            for action in candidates
            if action.action_type is ActionType.ESCALATE
        ]
        if escalations:
            return escalations[0]

        exploits = [
                action
            for action in candidates
        if (
        action.action_type is ActionType.EXPLOIT
        and not observation.current_host_compromised
       )
       ]
        if exploits:
            return exploits[0]

        discoveries = [
            action
            for action in candidates
            if action.action_type is ActionType.DISCOVER
        ]
        if discoveries:
            return discoveries[0]

        moves = [
            action
            for action in candidates
            if action.action_type is ActionType.MOVE
        ]
        if moves:
            return min(
                moves,
                key=lambda action: (
                    self._ROLE_PRIORITY.get(
                        observation.known_host_roles.get(action.target or ""),
                        99,
                    ),
                    action.target or "",
                ),
            )

        raise RuntimeError(
            "Red observation produced no heuristic candidate actions"
        )


class HeuristicBluePolicy:
    """Deterministic Blue baseline using only observable telemetry.

    Priority:
    1. Isolate a detected host with privilege-escalation evidence.
    2. Detect the oldest currently undetected telemetry target.
    3. Monitor when no response is justified by the observation.
    """

    def select_action(
        self,
        observation: BlueObservation,
        rng: random.Random,
    ) -> Action:
        escalation_hosts = []

        for event in observation.telemetry:
            if (
                event.event_type.value == "privilege_escalation"
                and event.source is not None
                and event.source in observation.detected_hosts
                and event.source not in observation.isolated_hosts
            ):
                if event.source not in escalation_hosts:
                    escalation_hosts.append(event.source)

        if escalation_hosts:
            return Action(
                agent=Agent.BLUE,
                action_type=ActionType.ISOLATE,
                target=escalation_hosts[0],
            )

        telemetry_targets = []
        for event in observation.telemetry:
            for target in (event.target, event.source):
                if target is not None and target not in telemetry_targets:
                    telemetry_targets.append(target)

        undetected = [
            target
            for target in telemetry_targets
            if target not in observation.detected_hosts
        ]

        if undetected:
            return Action(
                agent=Agent.BLUE,
                action_type=ActionType.DETECT,
                target=undetected[0],
            )

        return Action(
            agent=Agent.BLUE,
            action_type=ActionType.MONITOR,
        )