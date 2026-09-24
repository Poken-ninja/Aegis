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
- The initial compatibility checkpoint passed: 6 tests passed.

**Result:** `pyproject.toml` now declares Python `>=3.13,<3.15`.

**Rationale:** This allows the existing development environment to be used without introducing another Python installation while retaining an explicit upper bound for reproducibility.

**Limitation:** Python 3.15 is not claimed as supported. Compatibility with future Python versions will be evaluated deliberately rather than assumed.

## ADR-005 — Preserve design reasoning in version-controlled documentation

**Status:** Accepted

**Decision:** Maintain a detailed simulator design audit, architecture decision log, decision-evolution record, and chronological engineering log in the repository.

**Reason:** A research project must preserve not only implementation, but also the reasoning, corrections, failed tests, assumptions, scope decisions, and evidence that produced the implementation.

**Research implication:** Future work should be understandable from the repository without relying on chat history.

## ADR-006 — Discovery, movement, compromise, and privilege are distinct states

**Status:** Accepted

**Decision:** Do not treat discovery as compromise or discovery as unrestricted movement. Initial Internet-to-Web entry is an explicit exception; later internal movement requires an appropriate compromised foothold.

**Reason:** Otherwise compromise has little causal meaning in the simulated attack path.

## ADR-007 — Privilege requirements must affect attack paths

**Status:** Accepted

**Decision:** Synthetic vulnerabilities use different required privilege levels, and exploitation enforces those requirements.

**Reason:** A privilege field that never changes whether an action is possible is decorative rather than a cybersecurity mechanism.

**V1 privilege model:** `NONE → USER → ADMIN`.

**Capability interpretation:** `host_privileges` records where Red acquired a privilege during the episode. For V1, the attacker is also modeled as retaining its highest acquired privilege capability across compromised hosts. This is a deliberate abstraction that allows a privilege acquired on one compromised host to affect exploitation of another host without building a more complex credential/session model.

**Scope note:** This is a synthetic simulator abstraction, not a claim about how real enterprise credentials behave.

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

**Decision:** Generalization experiments must distinguish randomness used to generate a network configuration from randomness used for stochastic episode outcomes.

**Reason:** Network configuration is the independent research variable. Conflating configuration generation with episode randomness would make controlled comparisons harder to interpret.

**Configuration randomness:** Determines the synthetic enterprise configuration and its configuration identity/seed.

**Episode randomness:** Determines stochastic outcomes within an episode, such as exploit or escalation success.

**Experimental implication:** A held-out network configuration must not be accidentally recreated or altered by episode-level randomness. Experiments should record both configuration ID/seed and episode seed.

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

This section preserves how the simulator design changed as implementation and testing exposed weaknesses in earlier assumptions.

The purpose is not to label earlier work as failure. It is to preserve the chain of reasoning:

**assumption → implementation → evidence → revised decision → validation**

## Evolution 1 — Discovery versus movement

**Initial assumption:** A discovered adjacent host could be moved to.

**Evidence:** The model audit showed that discovery, position, compromise, and movement capability were being conflated.

**Problem:** If Red can freely traverse internal hosts after discovery, compromise becomes much less meaningful as a cybersecurity state transition.

**Revised decision:** Internet → Web is an explicit initial-entry exception. Subsequent internal movement requires the current Red position to be compromised and the target to be reachable/discovered.

**Validation:** A dedicated test rejects internal movement without a compromised foothold.

**Superseded by:** ADR-006.

## Evolution 2 — Privilege requirements become causal

**Initial assumption:** Vulnerabilities had a `required_privilege` field, but the initial configuration did not create sufficiently meaningful privilege-gated attack paths.

**Evidence:** A field that does not change action availability is decorative rather than causal.

**Revised decision:** Synthetic vulnerabilities can require NONE, USER, or ADMIN privilege, and exploitation checks Red's acquired privilege capability.

**Validation:** Tests cover NONE versus USER-required, USER versus USER-required, USER versus ADMIN-required, and ADMIN versus ADMIN-required exploitation.

**Superseded by:** ADR-007.

## Evolution 3 — Local privilege record versus attacker capability

**Initial implementation assumption:** `host_privileges` could be interpreted only as privilege local to the host where it was recorded.

**Evidence:** The intended V1 attack path requires a privilege acquired on one compromised host to influence what Red can exploit elsewhere. Modeling credentials, sessions, and transfer mechanics would add unnecessary complexity for the research question.

**Revised decision:** `host_privileges` records the acquisition location, while the current V1 attacker model retains its highest acquired privilege as a global capability for exploitation checks.

**Trade-off:** This intentionally abstracts away real credential/session semantics.

**Validation:** Tests directly assign USER or ADMIN capability on `web01` and verify its effect on exploitation of `app01` or `db01`.

**Status:** Accepted V1 abstraction; should be revisited only if it materially affects the generalization experiment.

## Evolution 4 — Critical asset victory condition

**Initial assumption:** Reaching the critical host was sufficient for Red victory.

**Evidence:** Reaching an asset and compromising an asset represent different simulated events.

**Problem:** The old condition could declare Red successful without a successful compromise.

**Revised decision:** Red wins only when the critical asset is actually in `compromised_hosts`.

**Validation:** One test verifies that reaching/attempting a failed critical exploit does not produce RED_WIN; another verifies successful critical compromise produces RED_WIN.

**Superseded by:** ADR-008.

## Evolution 5 — Timeout versus Blue victory

**Initial assumption:** A Red timeout could be interpreted as Blue success.

**Evidence:** Red failing to complete the objective does not prove that Blue detected, contained, isolated, or prevented Red.

**Revised decision:** TIMEOUT and BLUE_WIN are separate outcomes. Blue victory will require an explicit defensive success condition.

**Validation:** Current tests ensure timeout remains TIMEOUT rather than BLUE_WIN.

**Superseded by:** ADR-009.

## Evolution 6 — Randomness and reproducibility

**Initial assumption:** A single seed was sufficient as an informal reproducibility mechanism.

**Evidence:** The generalization experiment changes network configuration, while exploit/escalation outcomes are stochastic episode events. Mixing these sources of randomness could make it unclear whether an observed difference came from network configuration or episode randomness.

**Revised decision:** Treat configuration randomness and episode randomness as separate concepts. Record configuration ID/seed and episode seed independently.

**Additional evidence:** During ESCALATE testing, the first test run produced 52 collected, 49 passed, and 3 failed because the tests had incorrect assumptions about Python random-number sequences. The sequences were checked explicitly and the tests were corrected.

**Validation:** Current trajectory reproducibility testing checks identical state trajectories for the same seed and action sequence. Configuration-generation randomness remains an implementation requirement for the later generalization phase.

**Superseded by:** ADR-010 and ADR-011.

## Evolution 7 — Validate trajectories, not only terminal outcomes

**Initial assumption:** Matching final exploit success was sufficient to demonstrate deterministic behavior.

**Evidence:** Two simulations could reach the same final outcome through different intermediate states.

**Revised decision:** Reproducibility should compare relevant intermediate trajectory state as well as final outcome.

**Validation:** The test suite now compares position, discovered hosts, compromised hosts, privileges, step count, and outcome across identical seeded action sequences.

**Superseded by:** ADR-011.

## Evolution 8 — Deliberately test the tests

**Initial assumption:** A green test suite was sufficient evidence that the simulator was protected against regressions.

**Evidence:** A test suite can pass without proving that it detects a meaningful model violation.

**Revised decision:** Intentionally break an important invariant, verify a failing test, restore the implementation, and document the result.

**Observed validation:**

`60 passed` baseline  
→ foothold requirement intentionally removed  
→ `59 passed, 1 failed`  
→ `test_red_cannot_move_internally_without_compromised_foothold` failed  
→ rule restored  
→ `60 passed`

**Superseded by:** ADR-012.

## Evolution 9 — Test failures are evidence, not noise

**Initial assumption:** Early failing tests could simply be treated as obstacles to a green build.

**Evidence:** The 52-test ESCALATE checkpoint exposed incorrect assumptions about the random-number sequence associated with chosen seeds.

**Revised decision:** Preserve meaningful test failures in the engineering record, determine whether the failure comes from implementation, test assumptions, or model assumptions, and only then modify the appropriate artifact.

**Research implication:** Negative engineering results are part of the audit trail and should not be hidden by weakening tests.

## Evolution 10 — Simulator validation before learning

**Initial assumption:** It would be possible to begin RL development while the simulator was still being refined.

**Evidence:** The model audit identified multiple unresolved semantic issues in movement, privilege, victory, and reproducibility.

**Revised decision:** No RL or GPU training results are produced until the simulator passes its acceptance criteria.

**Research implication:** This protects the main experiment from measuring environment bugs instead of agent learning.

**Superseded by:** ADR-002.

## Research record principle

When a future decision changes an accepted design:

1. preserve the original decision and rationale;
2. record the evidence that motivated reconsideration;
3. document the revised decision;
4. identify which previous decision or assumption it supersedes;
5. add or update tests where appropriate;
6. record implementation implications;
7. record experimental implications and limitations.

This creates an auditable chain from **assumption → implementation → test/evidence → revision → validated design**.
