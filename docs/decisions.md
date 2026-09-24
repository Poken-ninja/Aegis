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

## ADR-005 — Preserve design reasoning in version-controlled documentation

**Status:** Accepted

**Decision:** Maintain a detailed simulator design audit and chronological engineering log in the repository.

**Reason:** A research project must preserve not only implementation, but also the reasoning, corrections, failed tests, assumptions, and scope decisions that produced the implementation.

**Research implication:** Future work should be understandable from the repository without relying on chat history.

## ADR-006 — Discovery, movement, compromise, and privilege are distinct states

**Status:** Accepted

**Decision:** Do not treat discovery as compromise or discovery as unrestricted movement. Initial Internet-to-Web entry is an explicit exception; later internal movement requires an appropriate compromised foothold.

**Reason:** Otherwise compromise has little causal meaning in the simulated attack path.

## ADR-007 — Privilege requirements must affect attack paths

**Status:** Accepted

**Decision:** Synthetic vulnerabilities must be allowed to require different privilege levels, and the simulator must enforce those requirements.

**Reason:** A privilege field that never changes whether an action is possible is decorative rather than a cybersecurity mechanism.

## ADR-008 — Red victory requires critical compromise

**Status:** Accepted

**Decision:** Red wins only when the critical asset is compromised.

**Reason:** Reaching a host and obtaining control are distinct simulated events.

## ADR-009 — Timeout is not Blue victory

**Status:** Accepted

**Decision:** TIMEOUT remains distinct from BLUE_WIN.

**Reason:** Blue victory must represent an actual defensive success, not merely Red failing to finish before the clock expires.

## ADR-010 — Separate configuration randomness from episode randomness

**Status:** Accepted for implementation planning

**Decision:** Generalization experiments should distinguish randomness used to generate a network configuration from randomness used for stochastic episode outcomes.

**Reason:** Network configuration is the independent research variable. Conflating configuration generation with episode randomness would make controlled comparisons harder to interpret.

## ADR-011 — Validate trajectories, not only final outcomes

**Status:** Accepted

**Decision:** Reproducibility testing should verify identical trajectories under the same configuration, episode seed, and action sequence.

**Reason:** Matching only the final outcome can hide divergent intermediate state transitions.

## ADR-012 — Deliberately test the tests

**Status:** Accepted

**Decision:** Before Phase 1 acceptance, intentionally introduce at least one controlled simulator defect, verify that tests detect it, then repair it and document the result.

**Reason:** Passing tests once does not establish that the test suite can detect meaningful regressions.
