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

**Phase 1 — Simulator**

Current work establishes a deterministic, testable network model before reinforcement learning is introduced.

## Repository structure

```text
src/aegis/
  network.py
tests/
  test_network.py
docs/
  research-question.md
  cybersecurity-model.md
  rules-of-engagement.md
  decisions.md
```

RL, multi-agent learning, topology variation, and held-out generalization experiments are intentionally deferred until the simulator semantics are accepted and the Phase-2 observation/action interface is explicitly defined.

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
- The current Blue detection primitive is not the final RL observation model.

No RL result is considered valid until the observation/action interface is specified and tested.
