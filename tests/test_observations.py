import pytest
from aegis.telemetry import TelemetryEvent, TelemetryType
from aegis.network import build_reference_network
from aegis.observations import (
    BlueObservation,
    RedObservation,
    build_blue_observation,
    build_red_observation,
)
from aegis.state import CyberState, PrivilegeLevel


def test_red_observation_records_allowed_information() -> None:
    observation = RedObservation(
        current_position="web01",
        discovered_hosts=frozenset({"web01", "app01"}),
        known_connections=frozenset(
            {
                ("web01", "app01"),
            }
        ),
        known_host_roles={
            "web01": "application",
            "app01": "application",
        },
        acquired_privilege="user",
    )

    assert observation.current_position == "web01"
    assert "web01" in observation.discovered_hosts
    assert observation.acquired_privilege == "user"


def test_blue_observation_records_allowed_information() -> None:
    observation = BlueObservation(
        known_hosts=frozenset({"web01", "app01"}),
        known_connections=frozenset(
            {
                ("web01", "app01"),
            }
        ),
        known_host_roles={
            "web01": "application",
            "app01": "application",
        },
        detected_hosts=frozenset({"web01"}),
    )

    assert "web01" in observation.known_hosts
    assert "web01" in observation.detected_hosts


def test_red_observation_has_no_ground_truth_compromise_field() -> None:
    observation = RedObservation(
        current_position="web01",
    )

    assert not hasattr(observation, "compromised_hosts")


def test_blue_observation_has_no_red_position_field() -> None:
    observation = BlueObservation()

    assert not hasattr(observation, "red_position")


def test_blue_observation_has_no_ground_truth_compromise_field() -> None:
    observation = BlueObservation()

    assert not hasattr(observation, "compromised_hosts")


def test_red_cannot_see_undiscovered_host() -> None:
    network = build_reference_network()
    state = CyberState(
        red_position="internet",
        discovered_hosts={"internet", "web01"},
    )

    observation = build_red_observation(network, state)

    assert "web01" in observation.discovered_hosts
    assert "db01" not in observation.discovered_hosts
    assert "critical01" not in observation.discovered_hosts


def test_red_cannot_see_undiscovered_host_role() -> None:
    network = build_reference_network()
    state = CyberState(
        red_position="internet",
        discovered_hosts={"internet", "web01"},
    )

    observation = build_red_observation(network, state)

    assert "web01" in observation.known_host_roles
    assert "db01" not in observation.known_host_roles
    assert "critical01" not in observation.known_host_roles


def test_red_cannot_see_connections_beyond_local_neighborhood() -> None:
    network = build_reference_network()
    state = CyberState(
        red_position="web01",
        discovered_hosts={"internet", "web01"},
    )

    observation = build_red_observation(network, state)

    assert ("internet", "web01") in observation.known_connections
    assert ("app01", "web01") in observation.known_connections
    assert ("app01", "db01") not in observation.known_connections


def test_red_cannot_see_vulnerabilities_on_undiscovered_hosts() -> None:
    network = build_reference_network()
    state = CyberState(
        red_position="web01",
        discovered_hosts={"internet", "web01"},
    )

    observation = build_red_observation(network, state)

    assert ("web01", "SYNTH_WEB_01") in observation.known_vulnerabilities
    assert ("app01", "SYNTH_APP_01") not in observation.known_vulnerabilities
    assert ("db01", "SYNTH_DB_01") not in observation.known_vulnerabilities
    assert ("critical01", "SYNTH_CRITICAL_01") not in observation.known_vulnerabilities


def test_red_cannot_see_remediation_on_undiscovered_host() -> None:
    network = build_reference_network()
    state = CyberState(
        red_position="web01",
        discovered_hosts={"internet", "web01"},
        remediated_vulnerabilities={"SYNTH_DB_01"},
    )

    observation = build_red_observation(network, state)

    assert "SYNTH_DB_01" not in observation.known_remediated_vulnerabilities


def test_red_cannot_see_isolation_of_undiscovered_host() -> None:
    network = build_reference_network()
    state = CyberState(
        red_position="web01",
        discovered_hosts={"internet", "web01"},
        isolated_hosts={"db01"},
    )

    observation = build_red_observation(network, state)

    assert "db01" not in observation.known_isolated_hosts


def test_red_observation_exposes_current_privilege_only() -> None:
    network = build_reference_network()
    state = CyberState(
        red_position="web01",
        discovered_hosts={"internet", "web01"},
        host_privileges={
            "web01": PrivilegeLevel.USER,
            "db01": PrivilegeLevel.ADMIN,
        },
    )

    observation = build_red_observation(network, state)

    assert observation.acquired_privilege == "user"


def test_blue_observation_does_not_expose_red_position() -> None:
    network = build_reference_network()
    state = CyberState(
        red_position="app01",
    )

    observation = build_blue_observation(network, state)

    assert not hasattr(observation, "red_position")


def test_blue_observation_does_not_expose_compromised_hosts() -> None:
    network = build_reference_network()
    state = CyberState(
        red_position="app01",
        compromised_hosts={"web01", "app01"},
    )

    observation = build_blue_observation(network, state)

    assert not hasattr(observation, "compromised_hosts")


def test_hidden_vulnerability_change_does_not_change_red_observation() -> None:
    network = build_reference_network()

    state = CyberState(
        red_position="web01",
        discovered_hosts={"internet", "web01"},
    )

    observation_before = build_red_observation(network, state)

    network.host("db01").vulnerabilities.clear()

    observation_after = build_red_observation(network, state)

    assert observation_before == observation_after


def test_hidden_isolation_change_does_not_change_red_observation() -> None:
    network = build_reference_network()

    state = CyberState(
        red_position="web01",
        discovered_hosts={"internet", "web01"},
    )

    observation_before = build_red_observation(network, state)

    state.isolated_hosts.add("db01")

    observation_after = build_red_observation(network, state)

    assert observation_before == observation_after


def test_hidden_remediation_change_does_not_change_red_observation() -> None:
    network = build_reference_network()

    state = CyberState(
        red_position="web01",
        discovered_hosts={"internet", "web01"},
    )

    observation_before = build_red_observation(network, state)

    state.remediated_vulnerabilities.add("SYNTH_DB_01")

    observation_after = build_red_observation(network, state)

    assert observation_before == observation_after


def test_blue_observation_receives_telemetry() -> None:
    network = build_reference_network()
    state = CyberState(red_position="internet")

    state.telemetry.append(
        TelemetryEvent(
            event_type=TelemetryType.EXPLOIT_ATTEMPT,
            source="web01",
            target="web01",
        )
    )

    observation = build_blue_observation(network, state)

    assert len(observation.telemetry) == 1
    assert observation.telemetry[0].event_type is TelemetryType.EXPLOIT_ATTEMPT
    assert observation.telemetry[0].source == "web01"
    assert observation.telemetry[0].target == "web01"


def test_blue_observation_does_not_expose_red_position() -> None:
    network = build_reference_network()
    state = CyberState(red_position="app01")

    observation = build_blue_observation(network, state)

    assert not hasattr(observation, "red_position")


def test_blue_observation_does_not_expose_compromised_hosts() -> None:
    network = build_reference_network()
    state = CyberState(red_position="app01")
    state.compromised_hosts.add("app01")

    observation = build_blue_observation(network, state)

    assert not hasattr(observation, "compromised_hosts")


def test_blue_observation_does_not_expose_red_privilege() -> None:
    network = build_reference_network()
    state = CyberState(red_position="app01")
    state.host_privileges["app01"] = PrivilegeLevel.ADMIN

    observation = build_blue_observation(network, state)

    assert not hasattr(observation, "host_privileges")
    assert not hasattr(observation, "acquired_privilege")


def test_hidden_red_position_does_not_change_blue_telemetry() -> None:
    network = build_reference_network()

    first_state = CyberState(red_position="web01")
    second_state = CyberState(red_position="critical01")

    telemetry = TelemetryEvent(
        event_type=TelemetryType.DISCOVERY_ACTIVITY,
        source="internet",
        target="web01",
    )

    first_state.telemetry.append(telemetry)
    second_state.telemetry.append(telemetry)

    first_observation = build_blue_observation(network, first_state)
    second_observation = build_blue_observation(network, second_state)

    assert first_observation.telemetry == second_observation.telemetry


def test_hidden_red_privilege_does_not_change_blue_telemetry() -> None:
    network = build_reference_network()

    first_state = CyberState(red_position="web01")
    second_state = CyberState(red_position="web01")

    first_state.host_privileges["web01"] = PrivilegeLevel.NONE
    second_state.host_privileges["web01"] = PrivilegeLevel.ADMIN

    telemetry = TelemetryEvent(
        event_type=TelemetryType.EXPLOIT_ATTEMPT,
        source="web01",
        target="web01",
    )

    first_state.telemetry.append(telemetry)
    second_state.telemetry.append(telemetry)

    first_observation = build_blue_observation(network, first_state)
    second_observation = build_blue_observation(network, second_state)

    assert first_observation.telemetry == second_observation.telemetry


def test_blue_observation_telemetry_is_immutable() -> None:
    network = build_reference_network()
    state = CyberState(red_position="internet")

    state.telemetry.append(
        TelemetryEvent(
            event_type=TelemetryType.LATERAL_MOVEMENT,
            source="web01",
            target="app01",
        )
    )

    observation = build_blue_observation(network, state)

    assert isinstance(observation.telemetry, tuple)

    with pytest.raises(AttributeError):
        observation.telemetry.append(  # type: ignore[attr-defined]
            TelemetryEvent(
                event_type=TelemetryType.DISCOVERY_ACTIVITY,
                source="internet",
                target="web01",
            )
        )
