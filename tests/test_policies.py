from aegis.actions import Action, ActionType, Agent
from aegis.network import build_reference_network
from aegis.observations import (
    BlueObservation,
    RedObservation,
    build_blue_observation,
    build_red_observation,
)
from aegis.policies import (
    RandomBluePolicy,
    RandomRedPolicy,
    blue_candidate_actions,
    red_candidate_actions,
)
from aegis.state import CyberState
from aegis.telemetry import TelemetryEvent, TelemetryType
import random


def test_initial_red_observation_supports_discovery_candidate() -> None:
    network = build_reference_network()
    state = CyberState(red_position="internet")

    observation = build_red_observation(network, state)
    candidates = red_candidate_actions(observation)

    assert candidates == (
        Action(
            agent=Agent.RED,
            action_type=ActionType.DISCOVER,
            target="web01",
        ),
    )


def test_red_candidate_generation_does_not_see_distant_topology() -> None:
    observation = RedObservation(
        current_position="web01",
        discovered_hosts=frozenset({"web01"}),
        known_connections=frozenset(
            {
                ("web01", "app01"),
            }
        ),
    )

    candidates = red_candidate_actions(observation)

    assert any(
        action.action_type is ActionType.DISCOVER
        and action.target == "app01"
        for action in candidates
    )
    assert all(action.target != "db01" for action in candidates)


def test_red_candidate_generation_can_move_to_discovered_neighbor() -> None:
    observation = RedObservation(
        current_position="web01",
        discovered_hosts=frozenset({"web01", "app01"}),
        known_connections=frozenset(
            {
                ("web01", "app01"),
            }
        ),
        current_host_compromised=True,
    )

    candidates = red_candidate_actions(observation)

    assert any(
        action.action_type is ActionType.MOVE
        and action.target == "app01"
        for action in candidates
    )


def test_red_candidate_generation_uses_only_observation_for_privilege() -> None:
    observation = RedObservation(
        current_position="app01",
        discovered_hosts=frozenset({"app01"}),
        current_host_compromised=True,
        acquired_privilege="user",
    )

    candidates = red_candidate_actions(observation)

    assert any(
        action.action_type is ActionType.ESCALATE
        and action.target == "app01"
        for action in candidates
    )


def test_red_candidate_generation_does_not_add_escalation_without_privilege() -> None:
    observation = RedObservation(
        current_position="app01",
        discovered_hosts=frozenset({"app01"}),
        acquired_privilege="none",
    )

    candidates = red_candidate_actions(observation)

    assert all(
        action.action_type is not ActionType.ESCALATE
        for action in candidates
    )


def test_blue_candidate_generation_always_has_monitor() -> None:
    observation = BlueObservation()

    candidates = blue_candidate_actions(observation)

    assert candidates == (
        Action(
            agent=Agent.BLUE,
            action_type=ActionType.MONITOR,
        ),
    )


def test_blue_candidate_generation_uses_telemetry_targets() -> None:
    observation = BlueObservation(
        telemetry=(
            TelemetryEvent(
                event_type=TelemetryType.EXPLOIT_ATTEMPT,
                source="app01",
                target="app01",
            ),
        )
    )

    candidates = blue_candidate_actions(observation)

    assert any(
        action.action_type is ActionType.DETECT
        and action.target == "app01"
        for action in candidates
    )


def test_blue_candidate_generation_uses_detected_hosts_for_response() -> None:
    observation = BlueObservation(
        detected_hosts=frozenset({"app01"}),
    )

    candidates = blue_candidate_actions(observation)

    assert any(
        action.action_type is ActionType.ISOLATE
        and action.target == "app01"
        for action in candidates
    )
    assert any(
        action.action_type is ActionType.REMEDIATE
        and action.target == "app01"
        for action in candidates
    )


def test_random_red_policy_is_reproducible() -> None:
    observation = RedObservation(
        current_position="web01",
        discovered_hosts=frozenset({"web01", "app01"}),
        known_connections=frozenset(
            {
                ("web01", "app01"),
            }
        ),
    )

    first = RandomRedPolicy().select_action(
        observation,
        random.Random(123),
    )
    second = RandomRedPolicy().select_action(
        observation,
        random.Random(123),
    )

    assert first == second


def test_random_blue_policy_is_reproducible() -> None:
    observation = BlueObservation(
        telemetry=(
            TelemetryEvent(
                event_type=TelemetryType.DISCOVERY_ACTIVITY,
                source="internet",
                target="web01",
            ),
        )
    )

    first = RandomBluePolicy().select_action(
        observation,
        random.Random(123),
    )
    second = RandomBluePolicy().select_action(
        observation,
        random.Random(123),
    )

    assert first == second


def test_random_red_never_selects_action_outside_candidate_set() -> None:
    observation = RedObservation(
        current_position="internet",
        known_connections=frozenset({("internet", "web01")}),
    )

    candidates = set(red_candidate_actions(observation))

    for seed in range(20):
        action = RandomRedPolicy().select_action(
            observation,
            random.Random(seed),
        )
        assert action in candidates


def test_random_blue_never_selects_action_outside_candidate_set() -> None:
    observation = BlueObservation()

    candidates = set(blue_candidate_actions(observation))

    for seed in range(20):
        action = RandomBluePolicy().select_action(
            observation,
            random.Random(seed),
        )
        assert action in candidates


def test_red_observation_local_neighbor_does_not_reveal_distant_edge() -> None:
    network = build_reference_network()
    state = CyberState(
        red_position="web01",
        discovered_hosts={"internet", "web01"},
    )

    observation = build_red_observation(network, state)

    assert ("app01", "web01") in observation.known_connections
    assert ("app01", "db01") not in observation.known_connections
