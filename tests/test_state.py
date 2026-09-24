import pytest

from aegis.state import CyberState, Outcome, PrivilegeLevel


def test_new_state_starts_in_progress() -> None:
    state = CyberState(red_position="internet")

    assert state.outcome is Outcome.IN_PROGRESS


def test_new_state_starts_at_step_zero() -> None:
    state = CyberState(red_position="internet")

    assert state.step_count == 0


def test_new_state_starts_with_empty_security_sets() -> None:
    state = CyberState(red_position="internet")

    assert state.discovered_hosts == set()
    assert state.compromised_hosts == set()
    assert state.detected_hosts == set()
    assert state.isolated_hosts == set()
    assert state.remediated_vulnerabilities == set()


def test_red_position_is_recorded() -> None:
    state = CyberState(red_position="web01")

    assert state.red_position == "web01"


def test_state_sets_are_independent_between_instances() -> None:
    first = CyberState(red_position="web01")
    second = CyberState(red_position="internet")

    first.compromised_hosts.add("web01")

    assert first.compromised_hosts == {"web01"}
    assert second.compromised_hosts == set()


def test_negative_step_count_is_rejected() -> None:
    with pytest.raises(ValueError):
        CyberState(red_position="internet", step_count=-1)


def test_new_state_starts_with_no_host_privileges() -> None:
    state = CyberState(red_position="internet")

    assert state.host_privileges == {}


def test_host_privilege_can_be_recorded() -> None:
    state = CyberState(red_position="web01")

    state.host_privileges["web01"] = PrivilegeLevel.USER

    assert state.host_privileges["web01"] is PrivilegeLevel.USER


def test_host_privileges_are_independent_between_states() -> None:
    first = CyberState(red_position="web01")
    second = CyberState(red_position="internet")

    first.host_privileges["web01"] = PrivilegeLevel.ADMIN

    assert second.host_privileges == {}


def test_new_state_starts_with_no_discovered_hosts() -> None:
    state = CyberState(red_position="internet")

    assert state.discovered_hosts == set()


def test_discovered_hosts_can_be_recorded() -> None:
    state = CyberState(red_position="internet")

    state.discovered_hosts.add("web01")

    assert state.discovered_hosts == {"web01"}


def test_discovered_hosts_are_independent_between_states() -> None:
    first = CyberState(red_position="internet")
    second = CyberState(red_position="internet")

    first.discovered_hosts.add("web01")

    assert second.discovered_hosts == set()