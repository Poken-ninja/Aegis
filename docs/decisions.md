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

## ADR-013 — Simulator errors are exceptions, not episode outcomes

**Status:** Accepted

**Decision:** `Outcome` contains only episode outcomes: `IN_PROGRESS`, `RED_WIN`, `BLUE_WIN`, and `TIMEOUT`. Invalid actions and invalid simulator/network configurations raise exceptions and are recorded separately by experiment infrastructure.

**Reason:** An implementation failure must never be interpreted as Red failure or Blue success. Keeping errors outside the episode outcome enum makes the experimental denominator explicit and prevents simulator defects from becoming performance data.

**Supersedes:** The earlier interpretation of `Outcome.ERROR` as a runtime episode state. ADR-004 remains the governing principle that simulator failures are separate from game outcomes.

## ADR-014 — `step_count` counts individual agent actions

**Status:** Accepted

**Decision:** One environment `step` is one successful Red or Blue action. `step_count` increments once per successful action. `max_steps` is therefore an action budget.

**Reason:** The primary time-to-objective and detection metrics need an unambiguous unit. Counting completed Red/Blue rounds would make the word 'steps' misleading and would complicate comparison with standard RL terminology.

**Research implication:** Red objective time and Blue detection time can be measured directly from the environment action count.

## ADR-015 — V1 Blue victory is containment

**Status:** Accepted

**Decision:** In V1, `BLUE_WIN` occurs only when Blue has detected and isolated Red's current non-critical host. Remediation alone does not produce `BLUE_WIN`.

**Reason:** The smallest defensible Blue objective is successful containment. A broader prevention/recovery model would add mechanisms not required by the core research question.

**Research implication:** Documentation must describe V1 Blue success as containment rather than claiming that all forms of prevention are modeled.

## ADR-016 — Agent observations are separate from hidden simulator state

**Status:** Accepted for Phase 2 design

**Decision:** The simulator maintains ground-truth cyber state, while Red and Blue will receive explicitly defined observations before RL training begins. Blue must not receive `compromised_hosts` directly as an observation.

**Reason:** Otherwise Blue could detect compromise by reading the simulator's hidden answer, making detection a bookkeeping operation rather than an autonomous decision problem.

**Implementation implication:** The current `DETECT` method remains a Phase-1 state-transition primitive. A Phase-2 observation layer must provide candidate evidence/signals that allow Blue to choose detection actions without direct access to hidden compromise state.

**Research implication:** Observation design is a prerequisite for meaningful Blue detection-time and defense-performance experiments.

## ADR-017 — Record successful action history in the environment

**Status:** Accepted

**Decision:** `AegisEnvironment` records the successful action sequence for the current episode in `action_history` and clears it on reset. Invalid actions are not recorded.

**Reason:** Reproducibility requires preserving the action sequence that generated a trajectory. Recording it at the simulator boundary reduces the risk of reconstructing trajectories incompletely in later experiment code.

**Research implication:** Experiment logs should still persist configuration ID/seed, episode seed, simulator parameters, and the action history.

## ADR-018 — Remove unused static host privilege metadata

**Status:** Accepted

**Decision:** Remove the unused `Host.privileges` field from the V1 network model. Dynamic Red privilege is represented only by `CyberState.host_privileges` and `PrivilegeLevel`.

**Reason:** The static field was not used by any transition rule and mixed host metadata with dynamic attacker capability. Keeping an unused security-looking field creates ambiguity about what actually affects the experiment.

**Research implication:** Every security-relevant state variable should either affect a defined transition/observation or be removed from V1.

## ADR-019 — Keep `MONITOR` as a Phase-1 placeholder

**Status:** Accepted for Phase 1; revisit before RL

**Decision:** Retain `MONITOR` in the conceptual Blue vocabulary for now, but do not treat the current no-op implementation as the final RL action semantics.

**Reason:** Blue monitoring is central to the cybersecurity concept, but inventing a complex telemetry system during simulator validation would expand scope. Before RL, `MONITOR` must either acquire a minimal causal observation effect or be excluded from the learning action space.

**Research implication:** No RL result may use the current no-op `MONITOR` action as if it represented realistic monitoring.

## ADR-020 — Define generalization at the configuration level

**Status:** Accepted for experiment design

**Decision:** A previously unseen evaluation case must have a configuration ID/seed withheld from training. We will distinguish instance-level novelty from distribution/family novelty and report which type is tested.

**Reason:** A new random seed from an identical configuration family is not automatically evidence of structural generalization. The research question is about previously unseen network configurations.

**Research implication:** The final experiment must specify the training configuration distribution, held-out evaluation set, and whether topology, vulnerability placement, privilege requirements, or other configuration attributes vary.

## ADR-021 — Control stochastic episode randomness in fixed-vs-diverse comparisons

**Status:** Accepted for experiment design

**Decision:** Fixed-training and diverse-training conditions will use matched evaluation episode seeds where practical, identical algorithm/hyperparameters, equal training-step budgets, and the same evaluation protocol.

**Reason:** The independent variable is training exposure to network configuration diversity. Uncontrolled differences in training budget, stochastic outcomes, or evaluation seeds would create confounds.

**Research implication:** Experiment metadata must record training condition, configuration IDs/seeds, episode seeds, algorithm settings, training steps, and evaluation seeds.
# Decision Backlog — Before Phase 2/RL

The following decisions are intentionally not all resolved during Phase 1. They are listed so the project does not silently make methodological choices during implementation.

## Must resolve before RL

1. **Observation model:** exact Red and Blue observations; what is hidden; how monitoring/detection evidence is generated.
2. **Action-space encoding:** how host-target actions map to a fixed action space when network configurations vary.
3. **Reward design:** separate Red and Blue rewards, terminal rewards, step costs, and whether reward shaping is allowed.
4. **Agent-learning setup:** independent policies, centralized training/decentralized execution, or another minimal MARL formulation.
5. **Interaction timing:** retain alternating Red→Blue turns or move to simultaneous actions. V1 currently uses alternating turns.
6. **Network variation dimensions:** topology, vulnerability placement, privilege requirements, host roles, or a controlled subset.
7. **Held-out definition:** instance-level unseen configurations versus unseen topology/configuration families.
8. **Training/evaluation split:** exact configuration IDs assigned to training, familiar evaluation, and unseen evaluation before training.
9. **Baseline agents:** random and deterministic heuristic baselines for Red and Blue before RL.
10. **RL algorithm/framework:** select only after the observation/action interface and baseline behavior are stable; PPO remains a candidate, not a commitment.

## Must resolve before the main experiment

11. **Training budget:** equal environment-action budget, episode budget, or another controlled unit.
12. **Evaluation protocol:** number of episodes per configuration and matched episode seeds where practical.
13. **Random seeds/replicates:** how many independent training seeds are used and how they are aggregated.
14. **Checkpoint selection:** how the evaluated model checkpoint is selected without leaking unseen-test performance into training decisions.
15. **Statistical analysis:** uncertainty reporting, aggregation across seeds/configurations, and appropriate comparisons.
16. **Generalization-gap formula:** metric-specific calculation and sign convention.
17. **Failure accounting:** how invalid actions, simulator exceptions, timeouts, and wins are reported without contaminating performance denominators.
18. **Compute budget:** when DGX Spark is used, how many training runs/parallel environments are justified, and what remains reproducible on CPU.
19. **Experiment artifact format:** exact files containing run metadata, configuration IDs/seeds, episode seeds, actions/trajectories, model checkpoints, metrics, and environment version.
20. **Reproducibility target:** exact software versions and configuration needed to reproduce reported tables/figures.

## Explicitly deferred unless the core experiment succeeds

21. Adversarial red→blue→red adaptation/self-play.
22. Richer incident-response mechanics.
23. Complex network generators.
24. Large-scale distributed training.
25. Additional agent memory or advanced policy architectures.

These backlog items are methodological controls, not feature requests. If an item does not materially affect the frozen research question, it should be simplified rather than expanded.
## Additional Phase-2 methodology decisions

22. **Opponent-training regime:** decide whether Red and Blue learn simultaneously, alternate training, or train against fixed/random/heuristic opponents. This affects whether observed generalization is attributable to network diversity or opponent co-adaptation.
23. **Evaluation opponent protocol:** specify which Red policy is used when evaluating Blue and which Blue policy is used when evaluating Red, including whether evaluation is symmetric or uses independently trained counterparts.
24. **Policy checkpoint pairing:** define whether Red and Blue checkpoints are paired by training iteration, independently selected, or evaluated against a fixed baseline opponent.
25. **Reward-information leakage:** ensure reward signals used during training do not reveal hidden network configuration or terminal information unavailable to the agent through its observation.
26. **Variable-size network interface:** determine whether V1 supports a fixed maximum number of hosts with masking/padding or a graph-native representation. The choice must permit evaluation on unseen configurations without changing the learned action/observation interface.
## ADR-027 — Controlled learning is the V1 primary learning regime

**Status:** Accepted for Phase 2 methodology

**Decision:** The main generalization experiment will use controlled learning rather than simultaneous Red/Blue co-adaptation. The primary comparison will isolate exposure to network-configuration diversity while controlling the opponent-training regime.

**Reason:** The frozen research question asks whether learned strategies generalize to previously unseen network configurations. If both agents learn simultaneously, changes in Red behavior can be caused by Blue adaptation and vice versa. That introduces opponent co-adaptation as a second major experimental variable and makes the effect of network diversity harder to interpret.

**Research implication:** The core experiment should make network diversity the principal manipulated training factor. Opponent behavior must be controlled and explicitly documented.

**Scope implication:** Simultaneous learning is not removed from the project; it is deferred to an extension after the core experiment succeeds.

## ADR-028 — Simultaneous Red/Blue learning is an extension, not the core experiment

**Status:** Accepted

**Decision:** A simultaneous-learning regime, in which Red and Blue update while interacting with each other, may be evaluated only after the controlled-learning experiment is complete and validated.

**Reason:** Simultaneous learning is cyber-research-relevant because it permits co-adaptation, but it introduces non-stationarity: each agent's learning target changes as the opponent policy changes. This makes causal interpretation and debugging substantially harder.

**Research implication:** If performed, simultaneous learning will be reported as a separate experiment with its own training protocol, budget, checkpoints, and interpretation. It must not replace the controlled experiment or be mixed into its primary results.

**Scope control:** If time runs short, this extension is dropped without changing the core research question or main experiment.

## ADR-029 — Separate episode termination from training termination

**Status:** Accepted

**Decision:** Individual episodes terminate through the simulator's existing terminal conditions (RED_WIN, BLUE_WIN, or TIMEOUT). Training itself terminates through a separately defined, pre-registered training budget.

**Reason:** A learning agent may participate in many episodes, so an episode-level stopping condition does not determine when learning stops. Separating the two prevents indefinite training and makes experimental comparisons reproducible.

**Research implication:** Report both episode limits and training budgets. Do not describe an agent as finished learning merely because a fixed number of episodes has elapsed.

## ADR-030 — Use an explicit training budget for fair comparisons

**Status:** Accepted for Phase 2 methodology

**Decision:** Fixed-training and diverse-training conditions will receive the same primary training budget, measured in environment actions unless a later methodological review establishes a better controlled unit.

**Reason:** Giving one condition substantially more interaction experience would confound the effect of network diversity with the amount of learning experience.

**Research implication:** The main comparison should keep algorithm, hyperparameters, training budget, evaluation protocol, and other relevant controls the same, with training exposure to network configurations as the principal difference.

**Scope note:** The exact numeric budget is not yet fixed. It must be selected after baseline behavior and RL throughput are measured and recorded before the main experiment.

## ADR-031 — Freeze policies before evaluation

**Status:** Accepted for Phase 2 methodology

**Decision:** At the end of a defined training run, the evaluated policy/checkpoint is frozen. Evaluation on familiar and unseen configurations does not continue updating the policy.

**Reason:** Evaluation must measure the learned policy under held-out conditions rather than mixing evaluation with additional learning.

**Research implication:** Checkpoint selection rules must be defined before the unseen evaluation is used, and unseen configurations must not influence training or checkpoint selection.

## ADR-032 — Freeze configuration splits before training

**Status:** Accepted for Phase 2 methodology

**Decision:** Training configurations, familiar evaluation configurations, and unseen evaluation configurations will be assigned configuration IDs/seeds and frozen before the main training runs.

**Reason:** Changing the held-out set after observing results would introduce test leakage and weaken the interpretation of generalization.

**Research implication:** The experiment record must preserve the exact configuration split and its generation parameters.

## ADR-033 — Evaluate both instance-level and family-level novelty when feasible

**Status:** Accepted for experiment planning

**Decision:** The project will distinguish two forms of unseen configuration: (1) an unseen instance from a known configuration family/distribution, and (2) an unseen topology/configuration family. The primary experiment should prioritize instance-level generalization; family-level generalization is an additional stronger test if the simulator and schedule support it.

**Reason:** A new seed can test generalization to a new instance, but it does not necessarily test structural generalization. Family-level novelty provides a stronger test of whether learned strategies transfer beyond familiar structural patterns.

**Research implication:** Results must label which novelty level is being evaluated rather than calling every new seed unseen topology.

## ADR-034 — Network variation must be controlled and recorded

**Status:** Accepted for experiment planning

**Decision:** Network configurations may vary across multiple cybersecurity-relevant attributes, including topology/connectivity, host roles, vulnerability placement, privilege requirements, segmentation, and critical-asset placement, but each generated configuration must record the actual parameter values.

**Reason:** The project wants meaningful configuration diversity, but uncontrolled variation can make difficulty differences impossible to diagnose.

**Research implication:** The configuration generator and experiment metadata must preserve a configuration vector/description so performance can later be interpreted against the network properties that produced it.

**Scope control:** Vary everything does not mean adding unlimited complexity. The generator will use a bounded, documented set of variation dimensions that can be tested within the 8-week project.

## ADR-035 — Opponent strength must be controlled during evaluation

**Status:** Accepted for experiment planning

**Decision:** Red and Blue generalization results will specify the opponent policy used during evaluation. Comparisons must not change opponent strength at the same time as the network-generalization condition without explicitly treating opponent strength as an experimental variable.

**Reason:** A lower Red attack-success rate could result from a stronger Blue opponent rather than better Red generalization. Likewise, higher Blue defense success could result from an easier Red opponent.

**Research implication:** Evaluation protocols must define which fixed, heuristic, learned, or paired policy is used as the opponent for each reported result.

## ADR-036 — Simultaneous training has a finite budget even though policies keep adapting

**Status:** Accepted for extension design

**Decision:** If simultaneous learning is run, Red and Blue may continue updating throughout training episodes, but the run ends at the same kind of explicit finite training budget used elsewhere. Episodes still end independently through the simulator terminal conditions.

**Reason:** Co-adaptation does not require indefinite training. A fixed budget provides a reproducible stopping point even when there is no natural moment at which both agents have permanently finished learning.

**Research implication:** Simultaneous-learning results must report the training budget and, where useful, checkpoint performance over training to show whether behavior is improving, unstable, or degrading.

## Phase-2 methodological direction

The current locked direction is therefore:

1. Build the observation/action interface.
2. Establish random and deterministic heuristic baselines.
3. Define controlled learning against explicitly specified opponents.
4. Train fixed-network and diverse-network conditions under equal training budgets.
5. Freeze policies and configuration splits.
6. Evaluate familiar and unseen configurations, distinguishing instance-level and family-level novelty.
7. Analyze generalization gaps and failure modes.
8. Only if the core experiment is successful, consider simultaneous Red/Blue learning as an extension.