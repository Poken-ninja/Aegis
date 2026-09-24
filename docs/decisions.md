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
- The Phase 1 test suite passed: 6 tests passed at the initial compatibility checkpoint.

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

**Observed validation:** The internal movement foothold rule was intentionally removed. The test suite changed from 60 passing tests to 59 passing and 1 failing test. The failing test was `test_red_cannot_move_internally_without_compromised_foothold`. After restoring the rule, all 60 tests passed again.

---

# Decision Evolution Record

## Why preserve superseded decisions?

Research engineering is not only the final implementation. Earlier decisions capture the assumptions under which the system was originally designed. When evidence from testing, model review, or implementation shows that an assumption is inadequate, the decision should be revised without erasing the historical reasoning.

AEGIS therefore records **decision evolution** rather than silently rewriting the past.

A superseded decision is not necessarily a mistake. It is evidence of how the research model became more precise.

## Evolution 1 — Movement permission

**Initial assumption:** A discovered adjacent host could be moved to.

**Evidence that changed the decision:** The cybersecurity model requires discovery, compromise, and movement to represent different concepts. Allowing discovery alone to authorize internal movement weakened the causal attack path.

**Revised decision:** Internet → Web is an explicit initial-entry exception. Subsequent internal movement requires a compromised foothold.

**Validation:** A dedicated test now verifies that internal movement without a compromised foothold is rejected.

**Status:** Original assumption superseded by ADR-006.

## Evolution 2 — Privilege requirements

**Initial assumption:** Vulnerabilities carried a `required_privilege` field, but the initial vulnerability configuration did not create meaningful privilege-gated attack paths.

**Evidence that changed the decision:** A privilege attribute that does not change whether exploitation is possible is decorative and does not contribute meaningful cybersecurity behavior.

**Revised decision:** Synthetic vulnerabilities use different privilege requirements, including USER and ADMIN requirements, and exploitation checks Red's acquired privilege capability.

**Validation:** Dedicated tests verify NONE/USER/ADMIN access against USER- and ADMIN-required vulnerabilities.

**Status:** Original implementation assumption superseded by ADR-007.

## Evolution 3 — Red victory condition

**Initial assumption:** Red reaching the critical host was sufficient for victory.

**Evidence that changed the decision:** Reaching an asset and compromising an asset represent different events. Treating them as equivalent would overstate Red's success and weaken the meaning of the critical asset.

**Revised decision:** Red wins only when the critical asset is actually compromised.

**Validation:** Dedicated tests verify both failed critical exploitation and successful critical exploitation.

**Status:** Original victory condition superseded by ADR-008.

## Evolution 4 — Test validation

**Initial assumption:** A passing test suite was sufficient evidence that the simulator's current implementation was behaving as intended.

**Evidence that changed the decision:** Passing tests do not demonstrate that the tests can detect meaningful regressions.

**Revised decision:** Deliberately break important simulator invariants, verify that the tests fail, restore the implementation, and retain the result in the research record.

**Validation:** The internal movement foothold rule was broken deliberately; 1 test failed as expected; the rule was restored; all 60 tests passed.

**Status:** Original testing assumption superseded by ADR-012.

## Research record principle

When a future decision changes an accepted design:

1. preserve the original decision and its rationale;
2. record the evidence that motivated reconsideration;
3. document the revised decision;
4. identify which previous decision or assumption it supersedes;
5. add or update tests where appropriate;
6. record the implementation and experimental implications.

This creates an auditable chain from **assumption → implementation → test/evidence → revision → validated design**.
