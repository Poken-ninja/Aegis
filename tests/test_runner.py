"""Tests for the public observation-to-action episode runner."""

import random

import pytest

from aegis.actions import Action, ActionType, Agent
from aegis.environment import AegisEnvironment
from aegis.policies import RandomBluePolicy, RandomRedPolicy
from aegis.runner import run_episode
from aegis.state import Outcome


def test_runner_records_red_then_blue_decisions() -> None:
    result = run_episode(
        AegisEnvironment(seed=0, max_steps=4),
        RandomRedPolicy(),
        RandomBluePolicy(),
        policy_seed=0,
    )

    assert result.steps
    assert result.steps[0].agent is Agent.RED
    if len(result.steps) > 1:
        assert result.steps[1].agent is Agent.BLUE
    assert result.steps[0].action.agent is Agent.RED


def test_runner_is_reproducible_for_same_seeds() -> None:
    first = run_episode(
        AegisEnvironment(seed=7, max_steps=10),
        RandomRedPolicy(),
        RandomBluePolicy(),
        policy_seed=11,
    )
    second = run_episode(
        AegisEnvironment(seed=7, max_steps=10),
        RandomRedPolicy(),
        RandomBluePolicy(),
        policy_seed=11,
    )

    assert first == second


class InvalidRedPolicy:
    def select_action(self, observation, rng: random.Random) -> Action:
        return Action(
            agent=Agent.RED,
            action_type=ActionType.MOVE,
            target="app01",
        )


def test_invalid_action_is_not_misclassified_as_simulator_outcome() -> None:
    result = run_episode(
        AegisEnvironment(seed=0),
        InvalidRedPolicy(),
        RandomBluePolicy(),
    )

    assert result.outcome is None
    assert result.termination_reason == "invalid_action"
    assert result.invalid_action_count == 1


class ExploitRedPolicy:
    def select_action(self, observation, rng: random.Random) -> Action:
        return Action(
            agent=Agent.RED,
            action_type=ActionType.EXPLOIT,
            target=observation.current_position,
        )


def test_runner_does_not_misclassify_simulator_error_as_invalid_action(monkeypatch) -> None:
    environment = AegisEnvironment(seed=0)

    def broken_privilege_check(current, required):
        raise ValueError("synthetic simulator configuration error")

    monkeypatch.setattr(environment, "_privilege_satisfies", broken_privilege_check)

    with pytest.raises(ValueError, match="synthetic simulator configuration error"):
        run_episode(
            environment,
            ExploitRedPolicy(),
            RandomBluePolicy(),
        )
