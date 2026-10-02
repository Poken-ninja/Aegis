from aegis.environment import AegisEnvironment
from aegis.network import build_reference_network
from aegis.policies import HeuristicBluePolicy, HeuristicRedPolicy
from aegis.runner import run_episode


network = build_reference_network(
    configuration_id="NET_00001",
    seed=0,
)

environment = AegisEnvironment(
    network=network,
    seed=0,
    max_steps=20,
)

result = run_episode(
    environment,
    HeuristicRedPolicy(),
    HeuristicBluePolicy(),
    policy_seed=0,
)

print(f"Outcome: {result.outcome}")
print(f"Termination: {result.termination_reason}")
print(f"Steps: {len(result.steps)}")
print()

for step in result.steps:
    print(
    f"{step.step_index:02d} "
    f"{step.agent.value:4s} "
    f"{step.action.action_type.value:10s} "
    f"target={step.action.target!s:10s} "
    f"red_position={step.resulting_state.red_position:10s} "
    f"compromised={sorted(step.resulting_state.compromised_hosts)} "
    f"privileges={dict(step.resulting_state.host_privileges)} "
    f"detected={sorted(step.resulting_state.detected_hosts)} "
    f"telemetry={[(event.event_type.value, event.source, event.target) for event in step.resulting_state.telemetry]}"
)