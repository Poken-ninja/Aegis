from aegis.actions import Action, ActionType, Agent


def test_red_actions_exist() -> None:
    assert {
        ActionType.DISCOVER,
        ActionType.EXPLOIT,
        ActionType.MOVE,
        ActionType.ESCALATE,
    } <= set(ActionType)


def test_blue_actions_exist() -> None:
    assert {
        ActionType.MONITOR,
        ActionType.DETECT,
        ActionType.ISOLATE,
        ActionType.REMEDIATE,
    } <= set(ActionType)


def test_agents_are_distinct() -> None:
    assert Agent.RED is not Agent.BLUE


def test_action_values_are_stable() -> None:
    assert ActionType.DISCOVER.value == "discover"
    assert ActionType.EXPLOIT.value == "exploit"
    assert ActionType.MOVE.value == "move"
    assert ActionType.ESCALATE.value == "escalate"

    assert ActionType.MONITOR.value == "monitor"
    assert ActionType.DETECT.value == "detect"
    assert ActionType.ISOLATE.value == "isolate"
    assert ActionType.REMEDIATE.value == "remediate"


def test_action_records_agent_type_and_target() -> None:
    action = Action(
        agent=Agent.RED,
        action_type=ActionType.EXPLOIT,
        target="web01",
    )

    assert action.agent is Agent.RED
    assert action.action_type is ActionType.EXPLOIT
    assert action.target == "web01"


def test_action_target_is_optional() -> None:
    action = Action(
        agent=Agent.RED,
        action_type=ActionType.DISCOVER,
    )

    assert action.target is None