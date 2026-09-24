# Simulator Design Audit

## Purpose

This document preserves the reasoning and design corrections made during Phase 1 of AEGIS so that the research context does not depend on chat history.

AEGIS is an 8-week undergraduate research prototype. The project is intentionally small: one research question, one controlled simulation, one main experiment, and reproducible measurements.

## Frozen research question

> Can autonomous red/blue agents learn strategies that generalize to previously unseen simulated enterprise network configurations?

The main independent variable is **network configuration**.

The planned comparison is:

1. agents trained on a fixed network configuration;
2. agents trained across diverse network configurations.

Both are evaluated on familiar and previously unseen configurations.

Primary metrics:

- Red attack success rate
- Red action steps to objective
- Blue defense success rate
- Blue detection time in environment actions
- Familiar-versus-unseen performance
- Generalization gap

No results are claimed before the experiments are actually run.

## Project scope

The environment is a synthetic enterprise network containing:

- hosts;
- connections;
- synthetic vulnerabilities;
- privileges;
- a critical asset;
- a Red simulated attacker;
- a Blue simulated defender.

Red and Blue use abstract simulation actions rather than real exploitation or real defensive commands.

Explicitly out of scope:

- real-world attacks;
- real exploitation;
- malware or phishing;
- LLM cybersecurity;
- CTI ingestion;
- AI-agent identity;
- automated vulnerability discovery;
- security investment optimization;
- commercial platform development;
- large knowledge graphs;
- unnecessary infrastructure;
- large attack libraries;
- complex distributed systems;
- intelligent experience memory in V1;
- adversarial curriculum/self-play in V1.

Optional red-to-blue-to-red adversarial adaptation is deferred until the core experiment works.

## Research discipline

The project distinguishes:

1. existing prior work;
2. existing framework capabilities;
3. AEGIS engineering work;
4. the research contribution;
5. experimental hypotheses.

No novelty claim is made without literature verification.

Negative results are valid results.

## Phase structure

The project uses major phases only:

0. Design
1. Simulator
2. Agents
3. RL
4. Interaction
5. Generalization
6. Experiments
7. Research Output

Within a phase, work is tracked as ordered tasks and acceptance criteria rather than many sub-phase labels.

## Simulator-first decision

The simulator must be validated before RL.

Reason:

If the environment's cybersecurity rules are incorrect, RL results can measure simulator bugs rather than learning.

Required workflow:

CONCEPT → BUILD → TEST → BREAK → DEBUG → UNDERSTAND → EXPERIMENT → DOCUMENT

PPO is only an initial candidate. The project does not commit to an RL algorithm until the environment is trustworthy.

## Network model

The current network is represented as a NetworkX graph.

The initial reference topology is intentionally small:

Internet → Web → App → DB → Critical

with a workstation connected to the application server.

The topology is a synthetic research abstraction, not a claim to represent a complete real enterprise.

Network configuration must eventually be varied while keeping the rest of the experimental design controlled.

## Cyber state model

The simulator distinguishes several concepts that must not be conflated:

- discovered_hosts: Red knows the host exists;
- red_position: where Red currently is;
- compromised_hosts: hosts Red has successfully compromised;
- host_privileges: where Red acquired synthetic privilege during the episode;
- detected_hosts: hosts/events known to Blue;
- isolated_hosts: hosts currently contained by Blue;
- remediated_vulnerabilities: vulnerabilities disabled by Blue.

Discovery is therefore not equivalent to compromise.

Position is not equivalent to control.

Privilege is not equivalent to simply being present on a host.

### V1 privilege capability abstraction

The V1 simulator uses:

NONE → USER → ADMIN

`host_privileges` records the host where the privilege was acquired. For exploitation checks, V1 treats Red as retaining the highest acquired privilege as an attacker capability across the episode.

This is deliberately simpler than modeling real credential/session semantics. It exists to make privilege causally affect attack paths without adding unnecessary complexity.

## Red action model

The current abstract Red actions are:

- DISCOVER
- MOVE
- EXPLOIT
- ESCALATE

The intended progression is conceptually:

DISCOVER → MOVE → EXPLOIT → COMPROMISE → ESCALATE

Discovery tells Red what exists.

Movement changes Red's position.

Exploitation attempts to obtain control.

Escalation changes Red's synthetic privilege capability.

## Important design correction: movement requires a foothold

An earlier implementation allowed Red to move between discovered hosts without requiring a compromised foothold.

That was identified as a model problem.

If Red can freely traverse the enterprise merely because hosts are discovered, compromise becomes much less meaningful as a cybersecurity state transition.

The corrected rule is:

- the initial Internet-to-Web entry is an explicit exception;
- after initial entry, movement to another internal host requires an appropriate compromised foothold and network connectivity;
- discovery alone does not grant lateral movement capability.

This rule is important because it makes compromise causally relevant to attack-path progression.

## Important design correction: privilege must be causal

The simulator contains synthetic privilege levels:

NONE → USER → ADMIN

The vulnerability attribute `required_privilege` affects whether Red can exploit a vulnerability.

It cannot be a decorative field.

The current reference configuration uses meaningful privilege requirements so that attack paths depend on acquired capability.

The simulator tests:

- NONE can exploit NONE-required vulnerabilities;
- NONE cannot exploit USER-required vulnerabilities;
- USER can exploit USER-required vulnerabilities;
- USER cannot exploit ADMIN-required vulnerabilities;
- ADMIN can exploit ADMIN-required vulnerabilities.

These are simulator parameters, not claims about real vulnerabilities.

## Exploitation and escalation randomness

Exploit and escalation outcomes are stochastic simulator events.

The environment uses a seeded random number generator so stochastic trajectories can be reproduced.

The current implementation uses explicit probabilities as engineering parameters. These values are not intended to represent empirical real-world probabilities.

During development, seed assumptions were explicitly checked after test failures exposed incorrect expectations about Python's random-number sequence.

Relevant values used to reason about deterministic tests included:

- seed 0 first value approximately 0.8444;
- seed 1 first approximately 0.1344 and second approximately 0.8474;
- seed 2 first approximately 0.9560;
- seed 3 first three approximately 0.2380, 0.5442, 0.3700.

These values were used to choose deterministic test cases; they are not experimental findings.

## Configuration randomness versus episode randomness

This distinction is important for the future generalization experiment.

### Configuration randomness

Configuration randomness is used to construct a synthetic network configuration. It determines properties of the network that are part of the independent research variable.

Each configuration should have:

- a configuration ID;
- a configuration seed;
- reproducible network-generation parameters.

### Episode randomness

Episode randomness controls stochastic events within a particular network configuration, such as exploit and escalation outcomes.

Each episode should record:

- configuration ID;
- configuration seed;
- episode seed;
- action sequence;
- relevant simulator parameters.

### Research implication

Configuration randomness and episode randomness must not be conflated.

If the research variable is network configuration, differences between fixed and diverse training should be attributable to the intended configuration distribution rather than an uncontrolled mixture of network-generation and episode randomness.

This separation will be implemented more fully when network variation is introduced in the generalization phase.

## Critical asset victory condition

A design error was identified in the initial terminal condition.

Reaching the critical host is not necessarily equivalent to compromising it.

The intended Red victory condition is:

Red wins when the critical asset has been successfully compromised.

Therefore, critical_host in compromised_hosts must determine Red victory, not merely red_position == critical_host.

Reaching the critical asset without compromising it must not automatically produce RED_WIN.

## Blue victory and timeout

A timeout is not automatically a Blue victory.

The simulator distinguishes:

- RED_WIN: Red achieved the defined objective;
- BLUE_WIN: Blue successfully suppressed/contained/prevented Red according to explicit defensive rules;
- TIMEOUT: neither side achieved a defined win before the step limit;
- ERROR: simulator/configuration failure.

This distinction is required for valid experimental interpretation.

## Blue action model

The planned abstract Blue actions are:

- MONITOR
- DETECT
- ISOLATE
- REMEDIATE

The Phase-1 implementation has only minimal Blue mechanics.

For V1, BLUE_WIN is deliberately defined as successful containment: Blue must detect and isolate Red's current non-critical host.

MONITOR is currently a no-op placeholder. DETECT is a low-level state-transition primitive that marks an already-compromised host as detected. These mechanics are sufficient for deterministic simulator testing but are not yet the final autonomous Blue observation/action interface.

Before RL, the project must define a separate Blue observation layer that does not expose the hidden compromised_hosts state directly.

## Partial observability

`discovered_hosts` is retained as an explicit state variable.

Red should not automatically receive complete knowledge of the network.

This is important because discovery is a cybersecurity concept and because a completely observable environment would remove an important source of decision-making difficulty.

The exact observation interface for RL is deferred until the simulator state transitions are validated.

## Turn and step semantics

The simulator alternates:

RED → BLUE → RED → BLUE ...

One environment step is one successful agent action.

Therefore:

- `step_count` counts individual successful agent actions;
- `max_steps` is an action budget;
- time-to-objective and detection-time metrics can use `step_count` directly;
- a terminal action is included in the count that produced the terminal outcome.

## Invalid actions versus simulator errors

An invalid agent action is rejected as invalid input.

A simulator/configuration failure raises a simulator exception.

Neither is an episode outcome, and neither is counted as Red or Blue performance.

The Outcome enum therefore contains only IN_PROGRESS, RED_WIN, BLUE_WIN, and TIMEOUT.

For example, an invalid target should not be counted as a Red loss.

## Reproducibility

The minimum reproducibility target is:

Same network configuration + same episode seed + same successful action sequence = identical simulator trajectory.

AegisEnvironment.action_history records the successful action sequence for the current episode and is cleared on reset.

The network owns configuration identity/seed; the environment seed is the episode seed. The fixed reference network does not use the episode seed to change its topology.

Trajectory reproducibility is stronger than matching only a final outcome.

The current test suite compares relevant intermediate state, including:

- Red position;
- discovered hosts;
- compromised hosts;
- acquired privileges;
- step count;
- outcome.

The future configuration-generation system must separately record configuration randomness from episode randomness.

## Testing strategy

The simulator must be tested independently of RL.

Current categories include:

- network construction;
- host and edge validation;
- cyber-state validation;
- action validation;
- discovery;
- initial entry;
- movement restrictions;
- compromise;
- privilege requirements;
- escalation;
- critical compromise;
- timeout;
- invalid actions;
- reproducibility.

Blue containment and complete Red/Blue scenario coverage remain future Phase 1 work because the Blue mechanics are intentionally minimal.

Integration/scenario tests are required before RL is introduced.

## Deliberate break/debug validation

The simulator was intentionally broken after the expanded test suite reached 60 passing tests.

The internal movement foothold rule was changed so movement was always allowed.

Observed result:

- 59 passed;
- 1 failed.

The failing test was:

`test_red_cannot_move_internally_without_compromised_foothold`

Pytest reported that the expected `ValueError` was not raised.

The original rule was restored:

`return current_position in self.state.compromised_hosts`

The full suite then returned to:

- 60 passed.

This demonstrates that the test suite can detect a meaningful cybersecurity-model regression.

This is an engineering validation result, not an RL or generalization result.

## Historical implementation checkpoint: ESCALATE

During development, ESCALATE was added to the Red action model.

The first test run after adding it produced:

- 52 tests collected;
- 49 passed;
- 3 failed.

The failures were caused by incorrect assumptions about Python random-number sequences in the test seeds.

The seed behavior was then checked explicitly, the test assumptions were corrected, and later execution produced the current 60-test passing checkpoint.

The failure history is retained because it records how deterministic test assumptions were debugged rather than silently rewritten.

## Decision evolution summary

The main simulator design evolved through several evidence-driven corrections:

1. **Discovery → movement** was revised so discovery does not automatically grant internal movement.
2. **Privilege metadata → causal privilege** was revised so required privilege actually gates exploitation.
3. **Local privilege record → attacker capability** was clarified so V1 retains highest acquired privilege without implementing complex credential/session mechanics.
4. **Reach critical → critical compromise** was revised so Red victory requires actual critical compromise.
5. **Timeout → Blue victory** was separated so timeout is not falsely interpreted as defensive success.
6. **Single informal seed → separated randomness** was revised so configuration and episode randomness are distinct concepts.
7. **Final-state reproducibility → trajectory reproducibility** was strengthened to compare intermediate state transitions.
8. **Green tests → deliberate test validation** was strengthened through an intentional simulator break.
9. **Failed tests as noise → failed tests as evidence** was adopted so debugging history remains part of the research record.
10. **Start RL early → simulator acceptance first** was reinforced after the model audit exposed semantic issues.

The detailed historical record is maintained in `docs/decisions.md` and `docs/experiment-log.md`.

## Current Phase 1 status

Phase 1 simulator semantics have now been reconciled with the implementation.

Current accepted properties:

1. reference network topology and critical-asset assumptions are tested;
2. Red discovery, movement, exploitation, escalation, and privilege gating are tested;
3. Blue detection, isolation, and remediation primitives are tested;
4. RED_WIN, BLUE_WIN, and TIMEOUT are distinct;
5. simulator errors are exceptions, not episode outcomes;
6. step_count counts individual successful agent actions;
7. successful action history is recorded for reproducibility;
8. deliberate-break validation has demonstrated that a meaningful movement invariant is test-protected;
9. documentation records the remaining Phase-2 observation decision.

Before RL, one major design boundary remains intentionally deferred rather than unresolved: the autonomous Red/Blue observation interface. That interface must be specified and tested before learning begins.

No RL, PPO, MARL, DGX training, network-generalization experiment, or performance result should be introduced until the observation/action interface is finalized and the simulator acceptance tests remain green.

## Scope-control rule

If a proposed feature does not directly support:

- the cybersecurity model;
- the frozen research question;
- the main experiment;
- testing;
- measurement; or
- reproducibility,

it should normally be deferred or removed.

The priority is a small trustworthy simulator and a defensible experiment, not feature count.
