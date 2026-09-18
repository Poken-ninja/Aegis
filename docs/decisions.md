# Architecture Decision Log

## ADR-001 — Use a graph-based synthetic network

**Status:** Accepted

**Decision:** Represent the AEGIS enterprise network with NetworkX.

**Reason:** The research question requires controlled variation of network configuration. A graph gives us an explicit representation of hosts and connectivity while remaining small enough to test deterministically.

**Cybersecurity meaning:** Connectivity determines which simulated attack paths and defensive containment relationships can exist.

**Research implication:** Network structure can later be varied independently from agent-learning machinery.

## ADR-002 — Build the simulator before RL

**Status:** Accepted

**Decision:** Validate network and cyber-state transitions before introducing PPO, MARL, or GPU training.

**Reason:** Learning results are only meaningful if the environment implements the intended cybersecurity rules.

## ADR-003 — Keep vulnerabilities synthetic

**Status:** Accepted

**Decision:** Vulnerabilities are simulator attributes such as SYNTH_WEB_01; they do not map to operational exploit procedures.

**Reason:** This keeps the experiment controlled, reproducible, and within the project's simulation-only rules of engagement.

## ADR-004 — Treat ERROR separately from game outcomes

**Status:** Accepted

**Decision:** Simulator failures are not counted as Red failures or Blue victories.

**Reason:** Mixing implementation failures with agent performance would invalidate the experimental interpretation.
