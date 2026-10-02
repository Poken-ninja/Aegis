"""Run controlled synthetic Red-vs-Blue episodes.

This module is intentionally small. It connects the public observation/policy
interfaces to the existing simulator without changing simulator semantics.
"""

from __future__ import annotations

import random
from copy import deepcopy
from dataclasses import dataclass
from typing import Literal

from aegis.actions import Action, Agent
from aegis.environment import AegisEnvironment, InvalidActionError
from aegis.observations import (
    BlueObservation,
    RedObservation,
    build_blue_observation,
    build_red_observation,
)
from aegis.policies import BluePolicy, RedPolicy
from aegis.state import CyberState, Outcome


Observation = RedObservation | BlueObservation
TerminationReason = Literal[
    "terminal_outcome",
    "invalid_action",
    "policy_error",
]


@dataclass(frozen=True)
class EpisodeStep:
    """One policy decision and the resulting simulator state."""

    step_index: int
    agent: Agent
    observation: Observation
    action: Action
    resulting_state: CyberState


@dataclass(frozen=True)
class EpisodeResult:
    """Research-facing record for one baseline episode."""

    configuration_id: str
    configuration_seed: int
    episode_seed: int
    outcome: Outcome | None
    termination_reason: TerminationReason
    steps: tuple[EpisodeStep, ...]
    invalid_action_count: int


def run_episode(
    environment: AegisEnvironment,
    red_policy: RedPolicy,
    blue_policy: BluePolicy,
    *,
    policy_seed: int | None = None,
) -> EpisodeResult:
    """Run one alternating Red/Blue episode from public observations.

    Invalid actions are recorded separately from simulator outcomes. They do
    not become Red losses, Blue wins, or timeouts.
    """

    environment.reset()

    policy_rng = random.Random(
        environment.seed if policy_seed is None else policy_seed
    )
    steps: list[EpisodeStep] = []
    invalid_action_count = 0

    while environment.state.outcome is Outcome.IN_PROGRESS:
        agent = environment.current_agent

        if agent is Agent.RED:
            observation = build_red_observation(
                environment.network,
                environment.state,
            )
            policy = red_policy
        else:
            observation = build_blue_observation(
                environment.network,
                environment.state,
            )
            policy = blue_policy

        try:
            action = policy.select_action(observation, policy_rng)
        except RuntimeError:
            return EpisodeResult(
                configuration_id=environment.network.configuration_id,
                configuration_seed=environment.network.seed,
                episode_seed=environment.seed,
                outcome=None,
                termination_reason="policy_error",
                steps=tuple(steps),
                invalid_action_count=invalid_action_count,
            )

        try:
            resulting_state = environment.step(action)
        except InvalidActionError:
            invalid_action_count += 1
            return EpisodeResult(
                configuration_id=environment.network.configuration_id,
                configuration_seed=environment.network.seed,
                episode_seed=environment.seed,
                outcome=None,
                termination_reason="invalid_action",
                steps=tuple(steps),
                invalid_action_count=invalid_action_count,
            )

        steps.append(
            EpisodeStep(
                step_index=resulting_state.step_count,
                agent=agent,
                observation=deepcopy(observation),
                action=action,
                resulting_state=deepcopy(resulting_state),
            )
        )

    return EpisodeResult(
        configuration_id=environment.network.configuration_id,
        configuration_seed=environment.network.seed,
        episode_seed=environment.seed,
        outcome=environment.state.outcome,
        termination_reason="terminal_outcome",
        steps=tuple(steps),
        invalid_action_count=invalid_action_count,
    )
