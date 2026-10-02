"""Research-facing measurement helpers for baseline episodes.

The baseline layer does not change simulator behavior. It summarizes outcomes
and trajectory metrics from completed episodes so baseline experiments can be
run reproducibly before RL is introduced.
"""

from __future__ import annotations

from dataclasses import dataclass
import time

from aegis.environment import AegisEnvironment
from aegis.policies import (
    HeuristicBluePolicy,
    HeuristicRedPolicy,
    RandomBluePolicy,
    RandomRedPolicy,
)
from aegis.runner import EpisodeResult, run_episode
from aegis.state import Outcome


@dataclass(frozen=True)
class BaselineSummary:
    """Aggregate results for one reproducible baseline run."""

    configuration_id: str
    configuration_seed: int
    episode_count: int
    valid_episode_count: int
    red_wins: int
    blue_wins: int
    timeouts: int
    invalid_action_episodes: int
    policy_error_episodes: int
    red_attack_success_rate: float | None
    blue_defense_success_rate: float | None
    red_actions_to_objective: tuple[int, ...]
    blue_detection_times: tuple[int, ...]
    episodes_per_second: float


def _detection_time(result: EpisodeResult) -> int | None:
    """Return latency from first observable activity to first detection.

    The metric uses only telemetry that was publicly observable to Blue. A
    detection does not require successful compromise because the simulator
    explicitly models detection of suspicious activity, including failed
    exploit attempts.
    """

    first_observable_step: dict[str, int] = {}

    for step in result.steps:
        for event in step.resulting_state.telemetry:
            for host_id in (event.source, event.target):
                if host_id is not None and host_id not in first_observable_step:
                    first_observable_step[host_id] = step.step_index

        if (
            step.agent.value == "blue"
            and step.action.action_type.value == "detect"
            and step.action.target is not None
            and step.action.target in first_observable_step
        ):
            return step.step_index - first_observable_step[step.action.target]

    return None


def summarize_baseline_results(
    results: list[EpisodeResult],
    *,
    elapsed_seconds: float,
) -> BaselineSummary:
    """Summarize completed baseline episodes without inventing outcomes."""

    if not results:
        raise ValueError("results must not be empty")
    if elapsed_seconds <= 0:
        raise ValueError("elapsed_seconds must be positive")

    configuration_ids = {result.configuration_id for result in results}
    configuration_seeds = {result.configuration_seed for result in results}

    if len(configuration_ids) != 1 or len(configuration_seeds) != 1:
        raise ValueError(
            "baseline summary requires one fixed configuration"
        )

    valid_results = [
        result
        for result in results
        if result.termination_reason == "terminal_outcome"
        and result.outcome is not None
    ]

    red_wins = sum(result.outcome is Outcome.RED_WIN for result in valid_results)
    blue_wins = sum(result.outcome is Outcome.BLUE_WIN for result in valid_results)
    timeouts = sum(result.outcome is Outcome.TIMEOUT for result in valid_results)

    successful_red_episodes = [
        result
        for result in valid_results
        if result.outcome is Outcome.RED_WIN
    ]

    detection_times = [
        detection_time
        for result in valid_results
        if (detection_time := _detection_time(result)) is not None
    ]

    valid_count = len(valid_results)

    return BaselineSummary(
        configuration_id=next(iter(configuration_ids)),
        configuration_seed=next(iter(configuration_seeds)),
        episode_count=len(results),
        valid_episode_count=valid_count,
        red_wins=red_wins,
        blue_wins=blue_wins,
        timeouts=timeouts,
        invalid_action_episodes=sum(
            result.termination_reason == "invalid_action"
            for result in results
        ),
        policy_error_episodes=sum(
            result.termination_reason == "policy_error"
            for result in results
        ),
        red_attack_success_rate=(
            red_wins / valid_count if valid_count else None
        ),
        blue_defense_success_rate=(
            blue_wins / valid_count if valid_count else None
        ),
        red_actions_to_objective=tuple(
            result.steps[-1].step_index
            for result in successful_red_episodes
        ),
        blue_detection_times=tuple(detection_times),
        episodes_per_second=len(results) / elapsed_seconds,
    )


def run_random_baseline(
    *,
    episode_count: int = 100,
    configuration_seed: int = 0,
    episode_seed_start: int = 0,
    max_steps: int = 50,
) -> BaselineSummary:
    """Run Random Red versus Random Blue on the reference configuration.

    Configuration randomness and episode randomness remain separate:
    configuration_seed identifies the network, while each episode uses
    episode_seed_start + episode_index.
    """

    if episode_count <= 0:
        raise ValueError("episode_count must be positive")

    from aegis.network import build_reference_network

    network = build_reference_network(
        configuration_id="NET_00001",
        seed=configuration_seed,
    )

    results: list[EpisodeResult] = []
    started = time.perf_counter()

    for episode_index in range(episode_count):
        environment = AegisEnvironment(
            network=network,
            seed=episode_seed_start + episode_index,
            max_steps=max_steps,
        )
        results.append(
            run_episode(
                environment,
                RandomRedPolicy(),
                RandomBluePolicy(),
                policy_seed=episode_seed_start + episode_index,
            )
        )

    elapsed = time.perf_counter() - started

    return summarize_baseline_results(
        results,
        elapsed_seconds=elapsed,
    )


def run_heuristic_baseline(
    *,
    episode_count: int = 100,
    configuration_seed: int = 0,
    episode_seed_start: int = 0,
    max_steps: int = 50,
) -> BaselineSummary:
    """Run deterministic heuristic Red versus Blue on the reference network."""

    if episode_count <= 0:
        raise ValueError("episode_count must be positive")

    from aegis.network import build_reference_network

    network = build_reference_network(
        configuration_id="NET_00001",
        seed=configuration_seed,
    )

    results: list[EpisodeResult] = []
    started = time.perf_counter()

    for episode_index in range(episode_count):
        episode_seed = episode_seed_start + episode_index
        environment = AegisEnvironment(
            network=network,
            seed=episode_seed,
            max_steps=max_steps,
        )
        results.append(
            run_episode(
                environment,
                HeuristicRedPolicy(),
                HeuristicBluePolicy(),
                policy_seed=episode_seed,
            )
        )

    elapsed = time.perf_counter() - started

    return summarize_baseline_results(
        results,
        elapsed_seconds=elapsed,
    )
