# AEGIS

**Autonomous Generalization Evaluation in Simulated enterprise environments**

AEGIS is an undergraduate cybersecurity research prototype investigating:

> **Can autonomous red/blue agents learn strategies that generalize to previously unseen simulated enterprise network configurations?**

The project uses a small, synthetic cyber environment. Red represents a simulated attacker and Blue represents a simulated defender. The primary research variable is **network configuration**.

## Research scope

AEGIS V1 compares agents trained on:

1. a fixed network configuration, and
2. diverse network configurations,

then evaluates both on familiar and previously unseen configurations.

Primary measures:

- Red attack success rate
- Red action steps to objective
- Blue defense success rate
- Blue detection time in environment actions
- familiar vs. unseen performance
- generalization gap

## Safety and rules of engagement

- All offensive behavior is synthetic and confined to the simulator.
- No real exploitation, credentials, malware, phishing, or unauthorized testing is part of the project.
- Synthetic vulnerabilities are abstract state variables, not real CVEs or exploitable software.
- Results describe behavior in the simulated environment and are not automatically claims about real enterprise security.

## Current status

**Phase 2 — Controlled learning methodology**

The simulator and public Red/Blue observation-policy boundary are implemented and validated. The current checkpoint is **136 tests collected / 136 passed**. Baseline experiment design and variable network configuration remain before RL training.

## Repository structure

```text
src/aegis/
  actions.py
  environment.py
  network.py
  observations.py
  policies.py
  runner.py
  state.py
  telemetry.py
tests/
  test_actions.py
  test_environment.py
  test_network.py
  test_state.py
docs/
  research-question.md
  cybersecurity-model.md
  rules-of-engagement.md
  decisions.md
  simulator-design-audit.md
  experiment-log.md
```

RL, topology variation, and held-out generalization experiments are intentionally deferred until baseline behavior, network-configuration generation, and the remaining RL interface decisions are validated.

## Development principle

**Build → Test → Break → Debug → Understand → Experiment → Document**

A simulator result is not accepted merely because code executes. It must have a defined cybersecurity meaning and a test that checks that meaning.


## Current simulator semantics

- One environment step is one successful Red or Blue action.
- Red and Blue alternate turns.
- RED_WIN requires compromise of the critical asset.
- BLUE_WIN means successful containment of Red's current non-critical host.
- TIMEOUT is distinct from Blue victory.
- Simulator/configuration errors are exceptions, not experimental outcomes.
- The environment records successful actions in action_history for reproducibility.
- Blue detection is evidence-based: observable telemetry can support detection even when an underlying Red action did not produce compromise.
- Blue containment/remediation still require detected compromise.
- The public baseline runner records invalid policy actions separately from experimental outcomes.

No RL result is considered valid until the observation/action interface is specified and tested.
