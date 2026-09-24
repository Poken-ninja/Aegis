# Experiment and Engineering Log

## 2026-09 — Phase 1 simulator foundation

### Project constraints

- 8-week undergraduate research project.
- Approximately 1–2 hours of work per day.
- One NVIDIA DGX Spark available.
- GPU use should only be introduced when parallel computation or training genuinely benefits from it.
- Offensive behavior remains synthetic and simulation-only.

### Research question

Can autonomous red/blue agents learn strategies that generalize to previously unseen simulated enterprise network configurations?

### Methodological decision

Build and validate the simulator before RL.

Reason: RL cannot compensate for an incorrect environment model.

### Initial implementation

Established:

- Python project structure;
- NetworkX graph-based network;
- synthetic hosts;
- synthetic vulnerabilities;
- cyber state;
- Red and Blue action definitions;
- turn-based environment;
- seeded stochastic behavior;
- explicit terminal outcomes;
- pytest test suite.

### Python compatibility issue

The original Python requirement excluded Python 3.14.

Development environment:

- Python 3.14.6
- NetworkX 3.6.1

The project requirement was changed to:

>=3.13,<3.15

This was documented as an explicit compatibility decision rather than silently changing the environment.

### ESCALATE implementation

Red escalation was added using the synthetic privilege model:

NONE → USER → ADMIN

Escalation is probabilistic and seeded.

### Test failure

After adding ESCALATE:

- 52 tests collected;
- 49 passed;
- 3 failed.

The failures were due to incorrect test-seed assumptions, not evidence that the simulator model itself was correct or incorrect.

The random-number sequences were checked explicitly and the tests were corrected accordingly.

### Important model audit

A broader review then identified several issues that must be corrected before Phase 1 acceptance:

1. Discovery was being treated too much like movement permission.
2. Internal movement did not yet require a compromised foothold.
3. required_privilege was not yet sufficiently causal because vulnerabilities defaulted to none.
4. Red victory was based on reaching the critical host rather than compromising it.
5. Blue behavior remained incomplete.
6. Timeout and Blue victory needed to remain separate.
7. Reproducibility needed to be defined at trajectory level.

These are design corrections, not experimental results.

### Test-suite expansion after model audit

The simulator tests were then extended to protect the revised cybersecurity model.

The added validation covers:

- the Internet → Web initial-entry exception;
- the requirement for a compromised foothold before internal movement;
- privilege-gated exploitation;
- cross-host attacker privilege capability;
- critical-asset compromise as the Red victory condition.

The resulting complete test suite contains 60 tests.

### Deliberate-break validation

#### Purpose

Validate that the automated tests detect a meaningful violation of the cybersecurity model rather than merely passing under the current implementation.

#### Baseline

Before deliberately breaking the simulator:

- Test suite: 60 passed.

#### Deliberate fault

The internal movement rule was intentionally changed so that movement was always permitted:

`return True`

This removed the requirement that Red have a compromised foothold before moving internally.

#### Expected behavior

The simulator model requires:

- Discovery does not imply compromise.
- Red may make the initial Internet → Web entry.
- Subsequent internal movement requires the current Red position to be compromised.

#### Observed result

After introducing the deliberate fault:

`59 passed, 1 failed`

The failing test was:

`test_red_cannot_move_internally_without_compromised_foothold`

Pytest reported:

`Failed: DID NOT RAISE <class 'ValueError'>`

This demonstrated that the test suite detected the intentional violation of the internal-movement foothold rule.

#### Restoration

The original movement rule was restored:

`return current_position in self.state.compromised_hosts`

The complete test suite then returned to:

`60 passed`

The final runtime varied slightly between runs (approximately 0.20–0.25 seconds); this variation is not treated as a research result.

#### Interpretation

The deliberate-break exercise provides evidence that the automated tests protect an important simulator invariant: network discovery alone does not grant Red the ability to move laterally through the simulated enterprise network.

This is a simulator validation result, not an experimental result about reinforcement learning or agent performance.

### Current status

Phase 1 is not yet accepted.

The simulator currently passes its 60-test suite, including a successful deliberate-break validation. Remaining Phase 1 work is to complete the simulator acceptance review, reconcile documentation with the final implementation, and confirm that the environment is sufficiently trustworthy before adding RL.

### Rule for reporting results

No learning performance, generalization result, attack success rate, or defense success rate will be reported until the corresponding experiment has actually been executed.

Failed tests and negative results will be retained as part of the research record.

## Simulator semantic reconciliation — 2026-09-24

The cross-check of documentation, implementation, and tests identified several semantic issues that needed explicit resolution before RL.

### Corrections

1. **Episode outcomes:** simulator/configuration errors are now exceptions rather than an Outcome.ERROR state. Experimental outcomes are limited to IN_PROGRESS, RED_WIN, BLUE_WIN, and TIMEOUT.
2. **Step semantics:** one environment step is one successful agent action. step_count now counts individual successful actions, making time-to-objective and detection-time metrics unambiguous.
3. **Trajectory reproducibility:** the environment now records successful actions in action_history; invalid actions are not recorded.
4. **Blue victory:** V1 BLUE_WIN is explicitly containment of Red's current non-critical host. It is not a general claim that all prevention or remediation produces victory.
5. **Host privilege metadata:** unused static host privilege metadata was removed. Dynamic Red privilege is represented by the cyber state.
6. **Observation boundary:** the current Blue DETECT primitive remains a Phase-1 state transition. Before RL, Blue must receive an explicit observation model that does not expose hidden compromise state directly.
7. **Experiment hypotheses:** H1 and H2 were added to the research question document.
8. **Experimental controls:** the decision log now requires matched evaluation seeds where practical, equal training budgets, identical algorithm/hyperparameters, and explicit configuration IDs/seeds.

### Research interpretation

These changes are engineering/model corrections. They are not learning results and do not support any claim about agent performance or generalization.

The simulator is now closer to a clean experimental instrument, but RL remains deferred until the Phase-2 observation/action interface is specified and tested.
## Phase-2 methodology lock — 2026-09-24

The project methodology was reviewed before RL planning. The following decisions are now locked for Phase 2 unless new evidence requires an explicit decision change.

### Primary learning regime

- The main experiment will use controlled learning rather than simultaneous Red/Blue co-adaptation.
- Network-configuration diversity remains the principal experimental variable.
- Opponent behavior and training conditions must be explicitly controlled and documented.

### Simultaneous learning extension

- Simultaneous Red/Blue learning is retained as an optional extension.
- It will only be attempted after the core fixed-vs-diverse experiment succeeds.
- It will be treated as a separate experiment because co-adaptation introduces non-stationarity and makes attribution harder.
- If time becomes constrained, the extension is removed rather than allowed to threaten the core experiment.

### Training and stopping

- An individual episode ends at RED_WIN, BLUE_WIN, or TIMEOUT.
- Training has a separate finite stopping condition: an explicit training budget.
- The primary budget will be measured in environment actions unless later methodology work establishes a better unit.
- Fixed-training and diverse-training conditions will receive equal primary training budgets.
- The exact numeric budget is intentionally not fixed yet; it will be selected after baseline/RL throughput measurements and documented before the main experiment.

### Evaluation and leakage control

- Policies are frozen before evaluation.
- Training, familiar-evaluation, and unseen-evaluation configuration splits will be frozen before the main training runs.
- Evaluation must not continue updating the evaluated policy.
- Unseen test configurations must not influence checkpoint selection.

### Unseen configurations

- The project distinguishes unseen instances from unseen configuration/topology families.
- Instance-level novelty is the primary generalization test.
- Family-level novelty is a stronger secondary test if feasible within the 8-week schedule.

### Network variation

- Configurations may vary across multiple recorded cybersecurity-relevant dimensions, such as topology/connectivity, host roles, vulnerability placement, privilege requirements, segmentation, and critical-asset placement.
- Variation will be bounded and documented rather than unlimited.
- Every generated configuration must preserve its configuration ID/seed and actual parameter description.

### Opponent control

- Reported Red and Blue results must specify the evaluation opponent.
- Opponent strength must not change silently between compared conditions.
- Fixed, heuristic, learned, or paired opponents may be used only with an explicit evaluation protocol.

### Methodological interpretation

These are experiment-design decisions, not learning results. No claim about generalization, agent strength, or performance follows from the decisions themselves.