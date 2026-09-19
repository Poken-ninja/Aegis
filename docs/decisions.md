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

## Python 3.14 compatibility

**Decision:** Support Python 3.13 and Python 3.14.

**Original constraint:** The project initially specified Python 3.13 only.

**Problem:** The development machine uses Python 3.14.6. The original constraint prevented installation of the project even though the pinned NetworkX 3.6.1 dependency could be downloaded successfully.

**Validation:**
- Python version: 3.14.6
- NetworkX version: 3.6.1
- AEGIS installed successfully after changing the Python requirement to `>=3.13,<3.15`.
- The Phase 1 test suite passed: 6 tests passed.

**Result:** `pyproject.toml` now declares Python `>=3.13,<3.15`.

**Rationale:** This allows the existing development environment to be used without introducing another Python installation while retaining an explicit upper bound for reproducibility.

**Limitation:** Python 3.15 is not claimed as supported. Compatibility with future Python versions will be evaluated deliberately rather than assumed.