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
- Red steps/time to objective
- Blue defense success rate
- Blue detection time
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
- host_privileges: Red's current synthetic privilege level on a host;
- detected_hosts: hosts/events known to Blue;
- isolated_hosts: hosts currently contained by Blue;
- remediated_vulnerabilities: vulnerabilities disabled by Blue.

Discovery is therefore not equivalent to compromise.

Position is not equivalent to control.

Privilege is not equivalent to simply being present on a host.

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

Escalation changes Red's synthetic privilege level.

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

The vulnerability attribute required_privilege must affect whether Red can exploit a vulnerability.

It cannot be a decorative field that is always none.

The intended model is that different synthetic vulnerabilities can require different privilege levels. For example, a vulnerability may require no privilege, user privilege, or administrative privilege.

These are simulator parameters, not claims about real vulnerabilities.

The simulator must test:

- NONE can exploit NONE-required vulnerabilities;
- NONE cannot exploit USER-required vulnerabilities;
- USER can exploit USER-required vulnerabilities;
- USER cannot exploit ADMIN-required vulnerabilities;
- ADMIN can exploit ADMIN-required vulnerabilities.

## Exploitation and escalation randomness

Exploit and escalation outcomes are stochastic simulator events.

The environment uses a seeded random number generator so that stochastic trajectories can be reproduced.

The current implementation uses explicit probabilities as engineering parameters. These values are not intended to represent empirical real-world probabilities.

Later experiments must record:

- configuration ID;
- configuration seed;
- episode seed;
- action sequence;
- relevant simulator parameters.

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

The initial implementation has only minimal Blue mechanics.

More detailed Blue behavior is deliberately deferred until the core simulator is stable. The project will not add a large incident-response system merely for realism.

The eventual Blue model must make defensive actions causally affect Red's ability to progress.

## Partial observability

discovered_hosts is retained as an explicit state variable.

Red should not automatically receive complete knowledge of the network.

This is important because discovery is a cybersecurity concept and because a completely observable environment would remove an important source of decision-making difficulty.

The exact observation interface for RL is deferred until the simulator state transitions are validated.

## Turn and step semantics

The simulator alternates:

RED → BLUE → RED → BLUE ...

step_count represents completed Red/Blue rounds rather than counting every individual action.

This must be documented and kept consistent when calculating time-to-objective metrics.

## Invalid actions versus simulator errors

An invalid agent action is rejected as invalid input.

A simulator/configuration failure is an ERROR.

These must not be mixed with Red or Blue performance outcomes.

For example, an invalid target should not be counted as a Red loss.

## Reproducibility

The minimum reproducibility target is:

Same network configuration + same episode seed + same action sequence = identical simulator trajectory.

The project already uses configuration IDs and seeded randomness.

A later refinement should clearly separate:

- randomness used to construct a network configuration;
- randomness used for stochastic episode outcomes.

This separation is important for generalization experiments because the network configuration itself is the research variable.

## Testing strategy

The simulator must be tested independently of RL.

Required categories include:

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
- Blue containment;
- timeout;
- invalid actions;
- reproducibility;
- configuration validity.

Integration/scenario tests are required before RL is introduced.

## Deliberate break/debug requirement

The simulator will not be considered trustworthy simply because its tests pass once.

At least one controlled defect or intentionally broken rule should be introduced, observed through a failing test, diagnosed, repaired, and documented.

This demonstrates that the test suite can detect an actual model regression.

## Current implementation checkpoint

During development, ESCALATE was added to the Red action model.

The first test run after adding it produced:

- 52 tests collected;
- 49 passed;
- 3 failed.

The failures were caused by incorrect assumptions about Python random-number sequences in the test seeds.

The seed behavior was then checked explicitly.

Relevant Python random values include:

- seed 0 first value approximately 0.8444;
- seed 1 first approximately 0.1344 and second approximately 0.8474;
- seed 2 first approximately 0.9560;
- seed 3 first three approximately 0.2380, 0.5442, 0.3700.

This supports using seed 3 for successful exploit/escalation progression and seed 1 for successful exploit followed by failed escalation under the current probabilities.

The corrected test file was prepared, but the final 52-test result must not be recorded as passing until it is actually executed and reported.

## Current known design gaps

Before Phase 1 can be accepted, the following must still be reconciled:

1. privilege requirements must be assigned meaningfully to synthetic vulnerabilities;
2. movement must enforce the compromised-foothold rule;
3. Red victory must require critical compromise;
4. minimal Blue mechanics must be implemented;
5. scenario/integration tests must cover complete attack/defense paths;
6. reproducibility must be tested at trajectory level;
7. configuration and episode randomness should be separated cleanly;
8. the simulator must undergo deliberate break/debug validation;
9. decisions and limitations must remain synchronized with implementation.

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
