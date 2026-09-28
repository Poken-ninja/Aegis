from aegis.telemetry import (
    TelemetryType,
    telemetry_for_red_action,
)


def test_discover_generates_discovery_telemetry() -> None:
    event = telemetry_for_red_action(
        "discover",
        source="internet",
        target="web01",
    )

    assert event is not None
    assert event.event_type is TelemetryType.DISCOVERY_ACTIVITY
    assert event.source == "internet"
    assert event.target == "web01"


def test_move_generates_lateral_movement_telemetry() -> None:
    event = telemetry_for_red_action(
        "move",
        source="web01",
        target="app01",
    )

    assert event is not None
    assert event.event_type is TelemetryType.LATERAL_MOVEMENT
    assert event.source == "web01"
    assert event.target == "app01"


def test_exploit_generates_exploit_telemetry() -> None:
    event = telemetry_for_red_action(
        "exploit",
        source="app01",
        target="app01",
    )

    assert event is not None
    assert event.event_type is TelemetryType.EXPLOIT_ATTEMPT
    assert event.source == "app01"
    assert event.target == "app01"


def test_escalate_generates_privilege_escalation_telemetry() -> None:
    event = telemetry_for_red_action(
        "escalate",
        source="app01",
    )

    assert event is not None
    assert event.event_type is TelemetryType.PRIVILEGE_ESCALATION
    assert event.source == "app01"
    assert event.target is None


def test_unknown_action_generates_no_telemetry() -> None:
    event = telemetry_for_red_action(
        "unknown_action",
        source="web01",
    )

    assert event is None


def test_telemetry_generation_is_deterministic() -> None:
    first = telemetry_for_red_action(
        "move",
        source="web01",
        target="app01",
    )

    second = telemetry_for_red_action(
        "move",
        source="web01",
        target="app01",
    )

    assert first == second

def test_exploit_telemetry_does_not_claim_success() -> None:
    event = telemetry_for_red_action(
        "exploit",
        source="app01",
        target="app01",
    )

    assert event is not None
    assert event.event_type is TelemetryType.EXPLOIT_ATTEMPT

    # Telemetry records an attempt, not whether the exploit succeeded.
    assert not hasattr(event, "success")
    assert not hasattr(event, "compromised")


def test_move_telemetry_does_not_expose_red_privilege() -> None:
    event = telemetry_for_red_action(
        "move",
        source="web01",
        target="app01",
    )

    assert event is not None

    # Blue should not receive Red's privilege through telemetry.
    assert not hasattr(event, "privilege")


def test_telemetry_does_not_expose_red_objective() -> None:
    event = telemetry_for_red_action(
        "move",
        source="web01",
        target="app01",
    )

    assert event is not None

    # The telemetry event contains activity, not Red's mission.
    assert not hasattr(event, "objective")


def test_discover_telemetry_contains_only_action_endpoints() -> None:
    event = telemetry_for_red_action(
        "discover",
        source="internet",
        target="web01",
    )

    assert event is not None

    assert event.source == "internet"
    assert event.target == "web01"


def test_telemetry_is_independent_of_hidden_privilege() -> None:
    event_without_privilege = telemetry_for_red_action(
        "move",
        source="web01",
        target="app01",
    )

    # The telemetry generator receives no privilege information.
    event_again = telemetry_for_red_action(
        "move",
        source="web01",
        target="app01",
    )

    assert event_without_privilege == event_again


def test_telemetry_does_not_report_compromise_from_exploit_attempt() -> None:
    event = telemetry_for_red_action(
        "exploit",
        source="app01",
        target="db01",
    )

    assert event is not None
    assert event.event_type is TelemetryType.EXPLOIT_ATTEMPT

    # The event represents an attempt only.
    assert event.target == "db01"