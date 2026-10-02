from aegis.baselines import run_random_baseline, summarize_baseline_results
from aegis.runner import run_episode
from aegis.environment import AegisEnvironment
from aegis.policies import RandomBluePolicy, RandomRedPolicy


def test_random_baseline_is_reproducible_except_throughput() -> None:
    first = run_random_baseline(
        episode_count=20,
        configuration_seed=3,
        episode_seed_start=10,
    )
    second = run_random_baseline(
        episode_count=20,
        configuration_seed=3,
        episode_seed_start=10,
    )

    assert first.configuration_id == second.configuration_id
    assert first.configuration_seed == second.configuration_seed
    assert first.episode_count == second.episode_count
    assert first.valid_episode_count == second.valid_episode_count
    assert first.red_wins == second.red_wins
    assert first.blue_wins == second.blue_wins
    assert first.timeouts == second.timeouts
    assert first.invalid_action_episodes == second.invalid_action_episodes
    assert first.policy_error_episodes == second.policy_error_episodes
    assert first.red_attack_success_rate == second.red_attack_success_rate
    assert first.blue_defense_success_rate == second.blue_defense_success_rate
    assert first.red_actions_to_objective == second.red_actions_to_objective
    assert first.blue_detection_times == second.blue_detection_times


def test_random_baseline_uses_fixed_reference_configuration() -> None:
    summary = run_random_baseline(
        episode_count=5,
        configuration_seed=17,
    )

    assert summary.configuration_id == "NET_00001"
    assert summary.configuration_seed == 17
    assert summary.episode_count == 5


def test_random_baseline_metrics_are_bounded() -> None:
    summary = run_random_baseline(
        episode_count=20,
        configuration_seed=0,
    )

    assert 0 <= summary.valid_episode_count <= summary.episode_count
    assert summary.red_wins + summary.blue_wins + summary.timeouts == (
        summary.valid_episode_count
    )

    if summary.red_attack_success_rate is not None:
        assert 0 <= summary.red_attack_success_rate <= 1

    if summary.blue_defense_success_rate is not None:
        assert 0 <= summary.blue_defense_success_rate <= 1

    assert summary.episodes_per_second > 0


def test_summary_rejects_mixed_configurations() -> None:
    first = run_episode(
        AegisEnvironment(seed=0, max_steps=4),
        RandomRedPolicy(),
        RandomBluePolicy(),
        policy_seed=0,
    )
    second_environment = AegisEnvironment(seed=1, max_steps=4)
    second_environment.network.configuration_id = "OTHER"
    second = run_episode(
        second_environment,
        RandomRedPolicy(),
        RandomBluePolicy(),
        policy_seed=1,
    )

    try:
        summarize_baseline_results(
            [first, second],
            elapsed_seconds=1.0,
        )
    except ValueError as exc:
        assert "one fixed configuration" in str(exc)
    else:
        raise AssertionError("mixed configurations must be rejected")
