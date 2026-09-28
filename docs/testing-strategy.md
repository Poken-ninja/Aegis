# AEGIS Testing Strategy

## Purpose

This document records what has actually been tested in the simulator, how those tests should be classified, what they establish, and what testing remains before RL.

The goal is not to claim that the simulator is "fully tested." The goal is to make the validation evidence explicit and reproducible.

## Testing layers used so far

AEGIS Phase 1 has primarily used **white-box testing**, with scenario/integration-style tests at the environment boundary.

### 1. White-box unit testing — implemented

The tests directly import and inspect internal classes and state.

Examples include:

- EnterpriseNetwork construction and validation;
- CyberState initialization and state-container independence;
- Action, Agent, and ActionType definitions;
- environment transition rules;
- privilege checks;
- terminal-condition logic;
- seeded stochastic behavior.

This is white-box because the tests know internal implementation structures such as CyberState, host_privileges, compromised_hosts, and the network graph.

### 2. White-box state-transition testing — implemented

The environment tests exercise specific cybersecurity transitions and invariants.

Covered areas include:

- discovery;
- initial Internet → Web entry;
- internal movement restrictions;
- compromise;
- privilege-gated exploitation;
- privilege escalation;
- critical-asset compromise;
- Blue detection;
- Blue isolation;
- Blue remediation;
- remediation blocking later exploitation;
- timeout;
- Red/Blue terminal precedence;
- action history;
- action-step counting;
- simulator/configuration error handling.

These tests validate the causal rules of the simulator rather than agent learning.

### 3. Scenario/integration testing through the environment API — implemented in limited form

Some tests exercise multiple actions in sequence through AegisEnvironment.step().

Examples include:

- moving Red to Web and exploiting it;
- exploiting and then escalating;
- detecting and then isolating a compromised host;
- remediating a host and verifying a later exploit is rejected;
- reproducing a trajectory using the same seed and action sequence.

These are integration-style tests because multiple simulator components interact.

They are not fully black-box tests because the test setup often manipulates internal simulator state directly.

### 4. Black-box testing — not yet sufficient

A true black-box test should interact with the system through its intended public interface without relying on internal state representation.

AEGIS does not yet have a complete observation/action interface, so a comprehensive black-box test layer is not possible yet.

Phase 2 should add public-interface tests such as:

- reset → observation;
- valid observation → valid action;
- action → new observation;
- terminal observation/action behavior;
- variable network configuration through the public interface;
- forbidden hidden state absent from observations.

The goal is to test what an agent can actually see and do without depending on internal simulator implementation.

### 5. Deliberate fault / mutation-like validation — implemented once

The simulator was intentionally modified so internal movement was always allowed.

Baseline:

- 60 tests passed.

Injected defect:

- internal movement foothold check removed.

Observed:

- 59 passed;
- 1 failed;
- failing test: test_red_cannot_move_internally_without_compromised_foothold.

The rule was restored. Later simulator additions expanded the suite, so the 60-test result is historical fault-injection evidence rather than the current suite size.

This is **not full automated mutation testing**. It is a deliberate fault-injection exercise demonstrating that at least one meaningful cybersecurity invariant is actually protected by a test.

### 6. Reproducibility testing — implemented

Tests check deterministic behavior under controlled conditions.

The intended reproducibility contract is:

> Same configuration + same episode seed + same successful action sequence = identical simulator trajectory.

The current tests compare relevant intermediate state including position, discovered hosts, compromised hosts, privileges, step count, and outcome.

### 7. Negative/error-path testing — implemented

Tests intentionally exercise invalid conditions and assert that the simulator rejects them.

Examples include:

- missing action targets;
- unknown hosts;
- self-connections;
- invalid movement;
- insufficient privilege;
- exploit after remediation;
- detection of an uncompromised host;
- isolation without detection;
- remediation without detection;
- invalid critical-host configuration.

These are important because invalid input must not silently become experimental outcomes.

## What we have NOT yet established

The current test suite does not establish:

- full black-box correctness;
- property-based testing;
- fuzz testing;
- automated mutation-testing score;
- performance/load testing;
- RL learning correctness;
- multi-agent learning stability;
- generalization performance;
- statistical validity of the future experiment;
- absence of every possible information-leakage path.

Those are separate validation questions.

## Current test inventory

The current repository contains:

- tests/test_network.py: 7 test functions;
- tests/test_state.py: 12 test functions;
- tests/test_actions.py: 6 test functions;
- tests/test_environment.py: 54 test functions.

## Current runtime test checkpoint

The latest verified pytest execution is:

- **74 tests collected**;
- **74 tests passed**;
- no test failures in that run.

This is the authoritative current runtime checkpoint for the simulator at the time of this document update.

An earlier static/manual count produced 79 apparent test functions, but pytest collected 74. The discrepancy is a bookkeeping/classification issue, not a simulator failure. The project will not report 79 tests passed. Before Phase-2 acceptance, the five non-collected definitions should be identified and the inventory reconciled without changing tests merely to make the numbers match.

## Phase 1 testing interpretation

The current evidence is strongest for:

1. local simulator invariants;
2. cybersecurity state-transition rules;
3. error handling;
4. deterministic trajectory reproducibility;
5. regression detection for at least one deliberately injected defect.

It is not yet evidence that the complete simulator is free of defects.

## Phase 2 testing requirements

Before RL training:

1. Run the complete current suite and record the actual result; the current verified checkpoint is 74 collected / 74 passed.
2. Add public-interface/black-box tests for the observation/action boundary.
3. Add information-leakage tests for both Red and Blue.
4. Add deterministic telemetry causality tests.
5. Add tests proving Blue-visible telemetry cannot directly expose hidden Red state.
6. Add tests for variable network configurations.
7. Re-run the deliberate-fault exercise after the observation layer exists.
8. Record failures and fixes in docs/experiment-log.md.

## Testing principle

AEGIS follows:

**CONCEPT → BUILD → TEST → BREAK → DEBUG → UNDERSTAND → EXPERIMENT → DOCUMENT**

A green test suite is evidence, not proof. Test coverage must be interpreted according to what was actually exercised and what remains untested.
