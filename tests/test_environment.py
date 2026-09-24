import pytest

from aegis.actions import Action, ActionType, Agent
from aegis.environment import AegisEnvironment
from aegis.state import Outcome, PrivilegeLevel


def test_reset_creates_initial_state() -> None:
    environment = AegisEnvironment(seed=42)

    state = environment.reset()

    assert state.red_position == "internet"
    assert state.step_count == 0
    assert state.outcome is Outcome.IN_PROGRESS
    assert environment.current_agent is Agent.RED


def test_turn_alternates_after_each_action() -> None:
    environment = AegisEnvironment(seed=42)
    environment.reset()

    red_action = Action(
        agent=Agent.RED,
        action_type=ActionType.DISCOVER,
        target="web01",
    )

    environment.step(red_action)

    assert environment.current_agent is Agent.BLUE
    assert environment.state is not None
    assert environment.state.step_count == 1

    blue_action = Action(
        agent=Agent.BLUE,
        action_type=ActionType.MONITOR,
    )

    environment.step(blue_action)

    assert environment.current_agent is Agent.RED
    assert environment.state.step_count == 2


def test_wrong_agent_cannot_act() -> None:
    environment = AegisEnvironment(seed=42)
    environment.reset()

    blue_action = Action(
        agent=Agent.BLUE,
        action_type=ActionType.MONITOR,
    )

    with pytest.raises(ValueError):
        environment.step(blue_action)


def test_environment_must_be_reset_before_step() -> None:
    environment = AegisEnvironment(seed=42)

    action = Action(
        agent=Agent.RED,
        action_type=ActionType.DISCOVER,
    )

    with pytest.raises(RuntimeError):
        environment.step(action)


def test_terminated_episode_cannot_continue() -> None:
    environment = AegisEnvironment(seed=42, max_steps=2)
    environment.reset()

    red_action = Action(
        agent=Agent.RED,
        action_type=ActionType.DISCOVER,
        target="web01",
    )

    blue_action = Action(
        agent=Agent.BLUE,
        action_type=ActionType.MONITOR,
    )

    environment.step(red_action)
    assert environment.state is not None
    assert environment.state.outcome is Outcome.IN_PROGRESS

    environment.step(blue_action)

    assert environment.state.outcome is Outcome.TIMEOUT

    with pytest.raises(RuntimeError):
        environment.step(red_action)


def test_invalid_max_steps_is_rejected() -> None:
    with pytest.raises(ValueError):
        AegisEnvironment(max_steps=0)


def test_red_can_discover_directly_reachable_host() -> None:
    environment = AegisEnvironment(seed=42)
    environment.reset()

    action = Action(
        agent=Agent.RED,
        action_type=ActionType.DISCOVER,
        target="web01",
    )

    state = environment.step(action)

    assert state.discovered_hosts == {"web01"}
    assert state.red_position == "internet"
    assert state.compromised_hosts == set()


def test_red_cannot_discover_non_adjacent_host() -> None:
    environment = AegisEnvironment(seed=42)
    environment.reset()

    action = Action(
        agent=Agent.RED,
        action_type=ActionType.DISCOVER,
        target="db01",
    )

    with pytest.raises(ValueError):
        environment.step(action)

    assert environment.state is not None
    assert environment.state.discovered_hosts == set()
    assert environment.state.red_position == "internet"


def test_discover_requires_a_target() -> None:
    environment = AegisEnvironment(seed=42)
    environment.reset()

    action = Action(
        agent=Agent.RED,
        action_type=ActionType.DISCOVER,
    )

    with pytest.raises(ValueError):
        environment.step(action)


def test_discover_does_not_compromise_host() -> None:
    environment = AegisEnvironment(seed=42)
    environment.reset()

    action = Action(
        agent=Agent.RED,
        action_type=ActionType.DISCOVER,
        target="web01",
    )

    state = environment.step(action)

    assert "web01" in state.discovered_hosts
    assert "web01" not in state.compromised_hosts


def test_red_can_make_initial_entry_to_discovered_web_host() -> None:
    environment = AegisEnvironment(seed=42)
    environment.reset()

    discover = Action(
        agent=Agent.RED,
        action_type=ActionType.DISCOVER,
        target="web01",
    )

    environment.step(discover)

    environment.step(
        Action(
            agent=Agent.BLUE,
            action_type=ActionType.MONITOR,
        )
    )

    move = Action(
        agent=Agent.RED,
        action_type=ActionType.MOVE,
        target="web01",
    )

    state = environment.step(move)

    assert state.red_position == "web01"
    assert state.discovered_hosts == {"web01"}
    assert state.compromised_hosts == set()


def test_red_cannot_move_internally_without_compromised_foothold() -> None:
    environment = AegisEnvironment(seed=42)
    environment.reset()

    environment.state.discovered_hosts.add("web01")
    environment.state.discovered_hosts.add("app01")
    environment.state.red_position = "web01"

    with pytest.raises(ValueError, match="compromised foothold"):
        environment.step(
            Action(
                agent=Agent.RED,
                action_type=ActionType.MOVE,
                target="app01",
            )
        )

    assert environment.state.red_position == "web01"


def test_red_cannot_move_to_undiscovered_host() -> None:
    environment = AegisEnvironment(seed=42)
    environment.reset()

    action = Action(
        agent=Agent.RED,
        action_type=ActionType.MOVE,
        target="web01",
    )

    with pytest.raises(ValueError):
        environment.step(action)

    assert environment.state is not None
    assert environment.state.red_position == "internet"


def test_red_cannot_move_to_non_adjacent_host() -> None:
    environment = AegisEnvironment(seed=42)
    environment.reset()

    environment.state.discovered_hosts.add("db01")

    action = Action(
        agent=Agent.RED,
        action_type=ActionType.MOVE,
        target="db01",
    )

    with pytest.raises(ValueError):
        environment.step(action)

    assert environment.state.red_position == "internet"


def test_red_cannot_move_to_isolated_host() -> None:
    environment = AegisEnvironment(seed=42)
    environment.reset()

    environment.state.discovered_hosts.add("web01")
    environment.state.isolated_hosts.add("web01")

    action = Action(
        agent=Agent.RED,
        action_type=ActionType.MOVE,
        target="web01",
    )

    with pytest.raises(ValueError):
        environment.step(action)

    assert environment.state.red_position == "internet"


def test_move_requires_a_target() -> None:
    environment = AegisEnvironment(seed=42)
    environment.reset()

    action = Action(
        agent=Agent.RED,
        action_type=ActionType.MOVE,
    )

    with pytest.raises(ValueError):
        environment.step(action)


def _move_red_to_web01(environment: AegisEnvironment) -> None:
    environment.reset()

    environment.step(
        Action(
            agent=Agent.RED,
            action_type=ActionType.DISCOVER,
            target="web01",
        )
    )

    environment.step(
        Action(
            agent=Agent.BLUE,
            action_type=ActionType.MONITOR,
        )
    )

    environment.step(
        Action(
            agent=Agent.RED,
            action_type=ActionType.MOVE,
            target="web01",
        )
    )

    environment.step(
        Action(
            agent=Agent.BLUE,
            action_type=ActionType.MONITOR,
        )
    )


def test_exploit_requires_a_target() -> None:
    environment = AegisEnvironment(seed=42)
    environment.reset()

    action = Action(
        agent=Agent.RED,
        action_type=ActionType.EXPLOIT,
    )

    with pytest.raises(ValueError):
        environment.step(action)


def test_exploit_requires_red_to_be_on_target() -> None:
    environment = AegisEnvironment(seed=42)
    environment.reset()

    environment.state.discovered_hosts.add("web01")

    action = Action(
        agent=Agent.RED,
        action_type=ActionType.EXPLOIT,
        target="web01",
    )

    with pytest.raises(ValueError):
        environment.step(action)


def test_exploit_requires_discovery() -> None:
    environment = AegisEnvironment(seed=42)
    environment.reset()

    environment.state.red_position = "web01"

    action = Action(
        agent=Agent.RED,
        action_type=ActionType.EXPLOIT,
        target="web01",
    )

    with pytest.raises(ValueError):
        environment.step(action)


def test_successful_exploit_can_compromise_host() -> None:
    environment = AegisEnvironment(seed=1)
    _move_red_to_web01(environment)

    action = Action(
        agent=Agent.RED,
        action_type=ActionType.EXPLOIT,
        target="web01",
    )

    state = environment.step(action)

    assert state.red_position == "web01"
    assert "web01" in state.discovered_hosts
    assert "web01" in state.compromised_hosts


def test_failed_exploit_does_not_compromise_host() -> None:
    environment = AegisEnvironment(seed=0)
    _move_red_to_web01(environment)

    action = Action(
        agent=Agent.RED,
        action_type=ActionType.EXPLOIT,
        target="web01",
    )

    state = environment.step(action)

    assert "web01" not in state.compromised_hosts


def test_remediated_vulnerability_cannot_be_exploited() -> None:
    environment = AegisEnvironment(seed=0)
    _move_red_to_web01(environment)

    environment.state.remediated_vulnerabilities.add("SYNTH_WEB_01")

    action = Action(
        agent=Agent.RED,
        action_type=ActionType.EXPLOIT,
        target="web01",
    )

    with pytest.raises(ValueError):
        environment.step(action)


def test_same_seed_and_actions_produce_same_exploit_result() -> None:
    first = AegisEnvironment(seed=1)
    second = AegisEnvironment(seed=1)

    _move_red_to_web01(first)
    _move_red_to_web01(second)

    action = Action(
        agent=Agent.RED,
        action_type=ActionType.EXPLOIT,
        target="web01",
    )

    first_state = first.step(action)
    second_state = second.step(action)

    assert first_state.compromised_hosts == second_state.compromised_hosts


def test_none_privilege_cannot_exploit_user_required_vulnerability() -> None:
    environment = AegisEnvironment(seed=3)
    environment.reset()

    environment.state.red_position = "app01"
    environment.state.discovered_hosts.add("app01")

    with pytest.raises(ValueError, match="required privilege"):
        environment.step(
            Action(
                agent=Agent.RED,
                action_type=ActionType.EXPLOIT,
                target="app01",
            )
        )


def test_user_privilege_can_exploit_user_required_vulnerability() -> None:
    environment = AegisEnvironment(seed=3)
    environment.reset()

    environment.state.red_position = "app01"
    environment.state.discovered_hosts.add("app01")
    environment.state.host_privileges["web01"] = PrivilegeLevel.USER

    state = environment.step(
        Action(
            agent=Agent.RED,
            action_type=ActionType.EXPLOIT,
            target="app01",
        )
    )

    assert "app01" in state.compromised_hosts


def test_user_privilege_cannot_exploit_admin_required_vulnerability() -> None:
    environment = AegisEnvironment(seed=3)
    environment.reset()

    environment.state.red_position = "db01"
    environment.state.discovered_hosts.add("db01")
    environment.state.host_privileges["web01"] = PrivilegeLevel.USER

    with pytest.raises(ValueError, match="required privilege"):
        environment.step(
            Action(
                agent=Agent.RED,
                action_type=ActionType.EXPLOIT,
                target="db01",
            )
        )


def test_admin_privilege_can_exploit_admin_required_vulnerability() -> None:
    environment = AegisEnvironment(seed=3)
    environment.reset()

    environment.state.red_position = "db01"
    environment.state.discovered_hosts.add("db01")
    environment.state.host_privileges["web01"] = PrivilegeLevel.ADMIN

    state = environment.step(
        Action(
            agent=Agent.RED,
            action_type=ActionType.EXPLOIT,
            target="db01",
        )
    )

    assert "db01" in state.compromised_hosts


def _move_red_to_web01_and_compromise(
    environment: AegisEnvironment,
) -> None:
    _move_red_to_web01(environment)

    environment.step(
        Action(
            agent=Agent.RED,
            action_type=ActionType.EXPLOIT,
            target="web01",
        )
    )

    environment.step(
        Action(
            agent=Agent.BLUE,
            action_type=ActionType.MONITOR,
        )
    )


def test_escalate_requires_a_target() -> None:
    environment = AegisEnvironment(seed=1)
    environment.reset()

    action = Action(
        agent=Agent.RED,
        action_type=ActionType.ESCALATE,
    )

    with pytest.raises(ValueError):
        environment.step(action)


def test_escalate_requires_compromised_host() -> None:
    environment = AegisEnvironment(seed=1)
    environment.reset()

    environment.state.red_position = "web01"
    environment.state.discovered_hosts.add("web01")

    action = Action(
        agent=Agent.RED,
        action_type=ActionType.ESCALATE,
        target="web01",
    )

    with pytest.raises(ValueError):
        environment.step(action)


def test_successful_escalation_grants_user_privilege() -> None:
    environment = AegisEnvironment(seed=3)
    _move_red_to_web01_and_compromise(environment)

    action = Action(
        agent=Agent.RED,
        action_type=ActionType.ESCALATE,
        target="web01",
    )

    state = environment.step(action)

    assert state.host_privileges["web01"].value == "user"


def test_failed_escalation_does_not_change_privilege() -> None:
    environment = AegisEnvironment(seed=1)
    _move_red_to_web01_and_compromise(environment)

    action = Action(
        agent=Agent.RED,
        action_type=ActionType.ESCALATE,
        target="web01",
    )

    state = environment.step(action)

    assert state.host_privileges.get("web01") is None


def test_escalation_can_progress_from_user_to_admin() -> None:
    environment = AegisEnvironment(seed=3)
    _move_red_to_web01_and_compromise(environment)

    first_escalation = Action(
        agent=Agent.RED,
        action_type=ActionType.ESCALATE,
        target="web01",
    )

    environment.step(first_escalation)

    environment.step(
        Action(
            agent=Agent.BLUE,
            action_type=ActionType.MONITOR,
        )
    )

    second_escalation = Action(
        agent=Agent.RED,
        action_type=ActionType.ESCALATE,
        target="web01",
    )

    state = environment.step(second_escalation)

    assert state.host_privileges["web01"].value == "admin"


def test_escalate_cannot_run_on_already_admin_host() -> None:
    environment = AegisEnvironment(seed=1)
    _move_red_to_web01_and_compromise(environment)

    environment.state.host_privileges["web01"] = PrivilegeLevel.ADMIN

    action = Action(
        agent=Agent.RED,
        action_type=ActionType.ESCALATE,
        target="web01",
    )

    with pytest.raises(ValueError):
        environment.step(action)


def test_reaching_critical_host_does_not_produce_red_win() -> None:
    environment = AegisEnvironment(seed=0)
    environment.reset()

    environment.state.red_position = "critical01"
    environment.state.discovered_hosts.add("critical01")
    environment.state.host_privileges["web01"] = PrivilegeLevel.ADMIN

    state = environment.step(
        Action(
            agent=Agent.RED,
            action_type=ActionType.EXPLOIT,
            target="critical01",
        )
    )

    assert "critical01" not in state.compromised_hosts
    assert state.outcome is Outcome.IN_PROGRESS


def test_compromising_critical_host_produces_red_win() -> None:
    environment = AegisEnvironment(seed=1)
    environment.reset()

    environment.state.red_position = "critical01"
    environment.state.discovered_hosts.add("critical01")
    environment.state.host_privileges["web01"] = PrivilegeLevel.ADMIN

    state = environment.step(
        Action(
            agent=Agent.RED,
            action_type=ActionType.EXPLOIT,
            target="critical01",
        )
    )

    assert "critical01" in state.compromised_hosts
    assert state.outcome is Outcome.RED_WIN

def test_blue_can_detect_compromised_host():
    env = AegisEnvironment(seed=1)
    env.reset()

    env.state.discovered_hosts.add("web01")
    env.state.compromised_hosts.add("web01")

    env.step(
        Action(
            agent=Agent.RED,
            action_type=ActionType.DISCOVER,
            target="web01",
        )
    )

    env.step(
        Action(
            agent=Agent.BLUE,
            action_type=ActionType.DETECT,
            target="web01",
        )
    )

    assert "web01" in env.state.detected_hosts


def test_blue_cannot_detect_uncompromised_host():
    env = AegisEnvironment(seed=1)
    env.reset()

    env.state.discovered_hosts.add("web01")

    env.step(
        Action(
            agent=Agent.RED,
            action_type=ActionType.DISCOVER,
            target="web01",
        )
    )

    with pytest.raises(ValueError):
        env.step(
            Action(
                agent=Agent.BLUE,
                action_type=ActionType.DETECT,
                target="web01",
            )
        )


def test_detection_does_not_automatically_isolate_host():
    env = AegisEnvironment(seed=1)
    env.reset()

    env.state.discovered_hosts.add("web01")
    env.state.compromised_hosts.add("web01")

    env.step(
        Action(
            agent=Agent.RED,
            action_type=ActionType.DISCOVER,
            target="web01",
        )
    )

    env.step(
        Action(
            agent=Agent.BLUE,
            action_type=ActionType.DETECT,
            target="web01",
        )
    )

    assert "web01" in env.state.detected_hosts
    assert "web01" not in env.state.isolated_hosts

def test_blue_can_isolate_detected_compromised_host():
    env = AegisEnvironment(seed=1)
    env.reset()

    env.state.discovered_hosts.add("web01")
    env.state.compromised_hosts.add("web01")
    env.state.detected_hosts.add("web01")

    env.step(
        Action(
            agent=Agent.RED,
            action_type=ActionType.DISCOVER,
            target="web01",
        )
    )

    env.step(
        Action(
            agent=Agent.BLUE,
            action_type=ActionType.ISOLATE,
            target="web01",
        )
    )

    assert "web01" in env.state.isolated_hosts


def test_blue_cannot_isolate_undetected_host():
    env = AegisEnvironment(seed=1)
    env.reset()

    env.state.discovered_hosts.add("web01")
    env.state.compromised_hosts.add("web01")

    env.step(
        Action(
            agent=Agent.RED,
            action_type=ActionType.DISCOVER,
            target="web01",
        )
    )

    with pytest.raises(ValueError, match="detected host"):
        env.step(
            Action(
                agent=Agent.BLUE,
                action_type=ActionType.ISOLATE,
                target="web01",
            )
        )


def test_isolation_does_not_remove_compromise():
    env = AegisEnvironment(seed=1)
    env.reset()

    env.state.discovered_hosts.add("web01")
    env.state.compromised_hosts.add("web01")
    env.state.detected_hosts.add("web01")

    env.step(
        Action(
            agent=Agent.RED,
            action_type=ActionType.DISCOVER,
            target="web01",
        )
    )

    env.step(
        Action(
            agent=Agent.BLUE,
            action_type=ActionType.ISOLATE,
            target="web01",
        )
    )

    assert "web01" in env.state.compromised_hosts
    assert "web01" in env.state.isolated_hosts


def test_red_cannot_move_into_isolated_host():
    env = AegisEnvironment(seed=1)
    env.reset()

    env.state.discovered_hosts.update({"web01", "app01"})
    env.state.compromised_hosts.add("web01")
    env.state.detected_hosts.add("web01")
    env.state.isolated_hosts.add("app01")
    env.state.red_position = "web01"

    with pytest.raises(ValueError, match="isolated"):
        env.step(
            Action(
                agent=Agent.RED,
                action_type=ActionType.MOVE,
                target="app01",
            )
        )


def test_red_cannot_move_from_isolated_host():
    env = AegisEnvironment(seed=1)
    env.reset()

    env.state.discovered_hosts.update({"web01", "app01"})
    env.state.compromised_hosts.update({"web01", "app01"})
    env.state.isolated_hosts.add("web01")
    env.state.red_position = "web01"

    with pytest.raises(ValueError, match="isolated host"):
        env.step(
            Action(
                agent=Agent.RED,
                action_type=ActionType.MOVE,
                target="app01",
            )
        )

def test_blue_can_remediate_detected_compromised_host():
    env = AegisEnvironment(seed=1)
    env.reset()

    env.state.discovered_hosts.add("web01")
    env.state.compromised_hosts.add("web01")
    env.state.detected_hosts.add("web01")

    env.step(
        Action(
            agent=Agent.RED,
            action_type=ActionType.DISCOVER,
            target="web01",
        )
    )

    env.step(
        Action(
            agent=Agent.BLUE,
            action_type=ActionType.REMEDIATE,
            target="web01",
        )
    )

    assert "SYNTH_WEB_01" in env.state.remediated_vulnerabilities


def test_blue_cannot_remediate_undetected_host():
    env = AegisEnvironment(seed=1)
    env.reset()

    env.state.discovered_hosts.add("web01")
    env.state.compromised_hosts.add("web01")

    env.step(
        Action(
            agent=Agent.RED,
            action_type=ActionType.DISCOVER,
            target="web01",
        )
    )

    with pytest.raises(ValueError, match="detected host"):
        env.step(
            Action(
                agent=Agent.BLUE,
                action_type=ActionType.REMEDIATE,
                target="web01",
            )
        )


def test_remediation_does_not_remove_existing_compromise():
    env = AegisEnvironment(seed=1)
    env.reset()

    env.state.discovered_hosts.add("web01")
    env.state.compromised_hosts.add("web01")
    env.state.detected_hosts.add("web01")

    env.step(
        Action(
            agent=Agent.RED,
            action_type=ActionType.DISCOVER,
            target="web01",
        )
    )

    env.step(
        Action(
            agent=Agent.BLUE,
            action_type=ActionType.REMEDIATE,
            target="web01",
        )
    )

    assert "web01" in env.state.compromised_hosts
    assert "SYNTH_WEB_01" in env.state.remediated_vulnerabilities

def test_remediation_prevents_red_from_exploiting_vulnerability():
    env = AegisEnvironment(seed=1)
    env.reset()

    env.state.discovered_hosts.add("web01")
    env.state.compromised_hosts.add("web01")
    env.state.detected_hosts.add("web01")
    env.state.red_position = "web01"

    env.step(
        Action(
            agent=Agent.RED,
            action_type=ActionType.EXPLOIT,
            target="web01",
        )
    )

    env.step(
        Action(
            agent=Agent.BLUE,
            action_type=ActionType.REMEDIATE,
            target="web01",
        )
    )

    assert "SYNTH_WEB_01" in env.state.remediated_vulnerabilities

    with pytest.raises(ValueError, match="no exploitable vulnerabilities"):
        env.step(
            Action(
                agent=Agent.RED,
                action_type=ActionType.EXPLOIT,
                target="web01",
            )
        )

def test_blue_wins_when_red_is_contained():
    env = AegisEnvironment(seed=1, max_steps=10)
    env.reset()

    env.state.red_position = "web01"
    env.state.compromised_hosts.add("web01")
    env.state.detected_hosts.add("web01")
    env.current_agent = Agent.BLUE

    env.step(
        Action(
            agent=Agent.BLUE,
            action_type=ActionType.ISOLATE,
            target="web01",
        )
    )

    assert "web01" in env.state.isolated_hosts
    assert env.state.outcome is Outcome.BLUE_WIN

def test_red_win_takes_precedence_over_blue_containment():
    env = AegisEnvironment(seed=1, max_steps=10)
    env.reset()

    env.state.red_position = "critical01"
    env.state.compromised_hosts.add("critical01")
    env.state.detected_hosts.add("critical01")
    env.state.isolated_hosts.add("critical01")
    env.current_agent = Agent.BLUE

    env.step(
        Action(
            agent=Agent.BLUE,
            action_type=ActionType.ISOLATE,
            target="critical01",
        )
    )

    assert env.state.outcome is Outcome.RED_WIN

def test_network_without_critical_host_raises_simulator_error() -> None:
    environment = AegisEnvironment(seed=42)
    environment.reset()
    environment.network.host("critical01").critical = False

    with pytest.raises(RuntimeError, match="exactly one critical host"):
        environment.step(
            Action(
                agent=Agent.RED,
                action_type=ActionType.DISCOVER,
                target="web01",
            )
        )


def test_network_with_multiple_critical_hosts_raises_simulator_error() -> None:
    environment = AegisEnvironment(seed=42)
    environment.reset()
    environment.network.host("web01").critical = True

    with pytest.raises(RuntimeError, match="exactly one critical host"):
        environment.step(
            Action(
                agent=Agent.RED,
                action_type=ActionType.DISCOVER,
                target="web01",
            )
        )


def test_action_history_records_successful_actions_only() -> None:
    environment = AegisEnvironment(seed=42)
    environment.reset()

    red_action = Action(
        agent=Agent.RED,
        action_type=ActionType.DISCOVER,
        target="web01",
    )

    environment.step(red_action)

    assert environment.action_history == [red_action]

    with pytest.raises(ValueError):
        environment.step(
            Action(
                agent=Agent.BLUE,
                action_type=ActionType.DETECT,
                target="web01",
            )
        )

    assert environment.action_history == [red_action]

    environment.reset()
    assert environment.action_history == []


def test_step_count_counts_individual_agent_actions() -> None:
    environment = AegisEnvironment(seed=42)
    environment.reset()

    environment.step(
        Action(
            agent=Agent.RED,
            action_type=ActionType.DISCOVER,
            target="web01",
        )
    )
    assert environment.state is not None
    assert environment.state.step_count == 1

    environment.step(
        Action(
            agent=Agent.BLUE,
            action_type=ActionType.MONITOR,
        )
    )
    assert environment.state.step_count == 2


def test_highest_acquired_privilege_applies_across_hosts() -> None:
    environment = AegisEnvironment(seed=3)
    environment.reset()

    environment.state.red_position = "app01"
    environment.state.discovered_hosts.add("app01")
    environment.state.host_privileges["web01"] = PrivilegeLevel.ADMIN

    state = environment.step(
        Action(
            agent=Agent.RED,
            action_type=ActionType.EXPLOIT,
            target="app01",
        )
    )

    assert "app01" in state.compromised_hosts
