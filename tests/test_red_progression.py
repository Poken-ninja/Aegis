"""Tests for the synthetic Red progression model."""

from aegis.actions import Action, ActionType, Agent
from aegis.environment import AegisEnvironment
from aegis.observations import build_red_observation
from aegis.state import PrivilegeLevel


def test_successful_exploit_creates_user_foothold() -> None:
    environment = AegisEnvironment(seed=1)
    environment.reset()
    environment.step(Action(Agent.RED, ActionType.DISCOVER, "web01"))
    environment.step(Action(Agent.BLUE, ActionType.MONITOR))
    environment.step(Action(Agent.RED, ActionType.MOVE, "web01"))
    environment.step(Action(Agent.BLUE, ActionType.MONITOR))
    environment.step(Action(Agent.RED, ActionType.EXPLOIT, "web01"))

    assert "web01" in environment.state.compromised_hosts
    assert environment.state.host_privileges["web01"] is PrivilegeLevel.USER


def test_movement_transfers_retained_privilege_to_target_host() -> None:
    environment = AegisEnvironment(seed=0)
    environment.reset()
    environment.state.red_position = "web01"
    environment.state.discovered_hosts.update({"web01", "app01"})
    environment.state.compromised_hosts.add("web01")
    environment.state.host_privileges["web01"] = PrivilegeLevel.USER

    environment.step(Action(Agent.RED, ActionType.MOVE, "app01"))

    assert environment.state.red_position == "app01"
    assert environment.state.host_privileges["app01"] is PrivilegeLevel.USER


def test_red_observation_exposes_compromise_of_current_host_only() -> None:
    environment = AegisEnvironment(seed=0)
    environment.reset()
    environment.state.red_position = "web01"
    environment.state.compromised_hosts.add("web01")

    observation = build_red_observation(environment.network, environment.state)

    assert observation.current_host_compromised is True


def test_random_red_does_not_offer_internal_move_without_foothold() -> None:
    from aegis.policies import red_candidate_actions

    environment = AegisEnvironment(seed=0)
    environment.reset()
    environment.state.red_position = "web01"
    environment.state.discovered_hosts.update({"web01", "app01"})

    observation = build_red_observation(environment.network, environment.state)
    candidates = red_candidate_actions(observation)

    assert all(
        not (
            action.action_type is ActionType.MOVE
            and action.target == "app01"
        )
        for action in candidates
    )
