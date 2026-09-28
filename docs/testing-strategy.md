# AEGIS Testing Strategy

## Purpose

This document records the validation methods used for the Phase 1 simulator, what they establish, and what remains outside Phase 1.

## Phase 1 testing layers

### 1. White-box unit testing — implemented

Tests directly inspect internal classes and state, including network construction, CyberState initialization, action definitions, and simulator configuration validation.

### 2. White-box state-transition testing — implemented

Covered simulator invariants include:
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
- terminal-condition precedence;
- action history;
- action-step counting;
- simulator/configuration error handling.

### 3. Scenario/integration-style testing — implemented in limited form

Selected tests execute multiple actions through `AegisEnvironment.step()` to verify interactions between network state, cyber state, action rules, and terminal conditions.

These tests are integration-style rather than fully black-box because some setup manipulates internal simulator state directly.

### 4. Negative/error-path testing — implemented

Invalid actions and invalid network configurations are intentionally exercised and rejected. Simulator errors are not converted into Red or Blue outcomes.

### 5. Reproducibility testing — implemented

The Phase 1 reproducibility contract is:

> Same configuration + same episode seed + same successful action sequence = identical simulator trajectory.

Tests compare relevant intermediate state as well as terminal outcome.

### 6. Deliberate fault injection — implemented once

The internal movement foothold rule was intentionally removed to verify that the test suite could detect a meaningful cybersecurity-model regression.

Historical result:
- 60 tests passed before the fault;
- 59 passed and 1 failed after the fault;
- the failing test was `test_red_cannot_move_internally_without_compromised_foothold`;
- restoring the rule returned the suite to 60 passed.

This is deliberate fault injection, not a full automated mutation-testing campaign.

## Phase 1 evidence boundary

Phase 1 testing establishes evidence about simulator correctness and reproducibility. It does not establish:
- RL learning correctness;
- multi-agent learning stability;
- network generalization;
- statistical validity of the future experiment;
- completeness of the future observation/action information boundary.

## Phase 1 runtime checkpoint

The documented Phase 1 runtime checkpoint is **74 tests collected and 74 passed**. Later Phase 2 tests are not included in this Phase 1 checkpoint.

## Deferred Phase 2 testing

Phase 2 is responsible for public agent-interface testing, observation leakage tests, synthetic telemetry causality tests, variable-configuration interface tests, and learning/baseline validation.

These are dependencies for the learning experiment and should not be presented as Phase 1 evidence.

## Testing principle

AEGIS follows:

**CONCEPT → BUILD → TEST → BREAK → DEBUG → UNDERSTAND → EXPERIMENT → DOCUMENT**

A green suite is evidence, not proof. Every claim must state what was actually exercised and what remains untested.