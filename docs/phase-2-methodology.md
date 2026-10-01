# Phase 2 — Controlled Learning Methodology

## Purpose

Phase 2 defines the agent-facing learning interface and the methodological controls required before reinforcement-learning training begins.

The frozen research question remains:

> Can autonomous red/blue agents learn strategies that generalize to previously unseen simulated enterprise network configurations?

Phase 2 is not yet an RL-results phase. Its purpose is to make the eventual learning experiment scientifically interpretable and reproducible.

## Phase 2 scope

The core Phase 2 work is:

1. define Red and Blue observations;
2. enforce information boundaries;
3. establish causal synthetic telemetry for Blue;
4. test the public observation boundary for leakage;
5. establish controlled baseline opponents;
6. define fixed-network versus diverse-network training;
7. define familiar and unseen configuration splits;
8. define equal training budgets;
9. freeze policies and configuration splits before evaluation;
10. prepare the smallest defensible RL experiment.

Simultaneous Red/Blue learning remains an optional extension and is not part of the core experiment.

## Current observation model

### Red

Red may observe:
- current position;
- discovered hosts;
- connections between discovered hosts;
- roles of discovered hosts;
- known vulnerabilities;
- known remediated vulnerabilities;
- known isolated hosts;
- Red's acquired privilege.

Red must not receive undiscovered topology or vulnerability information, Blue's hidden state, or future configuration information.

### Blue

Blue may observe:
- enterprise topology and host roles defined as part of its observation;
- synthetic telemetry;
- prior detections;
- isolated hosts;
- remediated vulnerabilities.

Blue must not receive:
- `red_position`;
- `compromised_hosts`;
- Red's hidden privilege state;
- other simulator ground truth that bypasses the intended evidence-based detection problem.

## Synthetic telemetry

Telemetry is synthetic evidence generated causally by valid Red actions.

Current event vocabulary:

| Red action | Blue-visible event |
|---|---|
| DISCOVER | `discovery_activity` |
| MOVE | `lateral_movement` |
| EXPLOIT | `exploit_attempt` |
| ESCALATE | `privilege_escalation` |

An `EXPLOIT` event represents an attempt, not a successful compromise.

Telemetry is stored internally as immutable `TelemetryEvent` objects. Blue receives the telemetry through its observation rather than through direct access to simulator state.

Invalid Red actions do not generate telemetry.

## Information-boundary validation

The observation layer is treated as an experimental-validity boundary, not merely a software convenience.

Tests currently cover:
- Blue receives telemetry events;
- expected event fields are preserved;
- Blue does not expose Red position;
- Blue does not expose compromised-host ground truth;
- Blue does not expose Red privilege;
- hidden Red position does not alter identical Blue telemetry;
- hidden Red privilege does not alter identical Blue telemetry;
- Blue's telemetry observation is immutable.

These tests complement earlier Red and Blue observation leakage tests.

## Learning methodology locked so far

### Primary regime

The core experiment uses controlled learning rather than simultaneous Red/Blue co-adaptation.

The principal manipulated training factor is exposure to network-configuration diversity.

### Training conditions

The main comparison is:
- fixed-network training;
- diverse-network training.

Both conditions must receive the same primary training budget unless a documented methodological review changes the unit of comparison.

The exact numeric budget is not yet fixed. It will be selected after baseline behavior and RL throughput are measured.

### Evaluation

Policies are frozen before evaluation.

Configuration splits are frozen before training and contain:
- training configurations;
- familiar evaluation configurations;
- unseen evaluation configurations.

Unseen configurations must not influence training or checkpoint selection.

### Novelty levels

The experiment distinguishes:

1. unseen instance from a known configuration family;
2. unseen configuration/topology family.

Instance-level generalization is the primary target. Family-level generalization is a stronger secondary test if time and simulator support permit it.

### Opponent control

Reported Red and Blue results must identify the opponent policy used during evaluation. Opponent strength must not change at the same time as the network-generalization condition unless opponent strength is explicitly treated as another experimental variable.

## Current evidence

The latest verified local test result is maintained from actual pytest execution, not from static test-function counts. The most recent pre-freeze run reported **136 collected / 136 passed**; a subsequent test correction added one test, so the current branch requires a fresh local full-suite run before a new passing count is recorded.

This remains engineering validation only. It is not an RL result and does not establish generalization.

No PPO, MARL, DGX training, or generalization performance result has been produced.

## Research-design freeze

The full V1 protocol is now specified in `docs/research-design-freeze.md`.

The core hypotheses are:

- **H1:** diverse-network training should produce smaller familiar-to-unseen performance degradation than fixed-network training under matched controls.
- **H2:** diverse-network training should produce better unseen-network performance than fixed-network training under matched controls.

The primary independent variable is training exposure to network-configuration diversity.

Primary Red metrics:
- attack success rate;
- actions to objective on successful attacks;
- familiar-to-unseen degradation.

Primary Blue metrics:
- defense/containment success rate;
- detection time;
- familiar-to-unseen degradation.

The V1 analysis reports raw familiar and unseen values and a direction-normalized degradation measure. No composite score is used.

The core evaluation uses controlled opponents. Simultaneous Red/Blue co-adaptation is deferred.

## Research contribution boundary

AEGIS does not claim novelty for:
- simulated cyber-agent RL itself;
- Red/Blue simulation itself;
- generalization to novel cyber scenarios itself;
- PPO or another RL algorithm.

The candidate contribution is the controlled empirical comparison of fixed versus diverse network-configuration training for Red and Blue policies under held-out configuration evaluation. This remains provisional pending the final literature review.

## Baseline action-validity rule

Blue detection is evidence-based. A `DETECT` action is valid when the target has observable synthetic telemetry, regardless of whether the underlying Red action successfully compromised the host. `ISOLATE` and `REMEDIATE` remain dependent on detected compromise because those actions change defensive state around an actual compromised host.

This prevents the baseline policy from needing hidden `compromised_hosts` information merely to avoid invalid detection actions. Invalid actions remain separately recorded by the episode runner.

## Experimental controls now frozen

The main experiment must hold constant simulator/version, observation/action model, reward formulation, RL algorithm, policy architecture, hyperparameters, primary training action budget, episode limit, configuration-generation distribution, configuration splits, evaluation seeds, checkpoint-selection rule, and opponent protocol. The only planned primary difference is fixed versus diverse training exposure.

The exact training budget and number of independent training seeds remain intentionally unfixed until throughput measurement. They must be frozen before the main experiment.

## Phase 2 limitations

The following remain unfinished:
- complete public environment observation/action API;
- controlled random and heuristic baselines;
- variable network configuration generator;
- finalized action/observation encoding for RL;
- RL algorithm selection;
- numeric training budget;
- training runs;
- familiar/unseen evaluation;
- statistical analysis;
- generalization results.

## Research integrity rule

Phase 2 must not report:
- learning performance before training is executed;
- generalization before held-out evaluation is executed;
- novelty claims without comparison to relevant prior work;
- simulator test counts as RL evidence.

Negative results, failed experiments, and implementation failures remain part of the research record.

## Next engineering checkpoint

Before RL:
1. complete and test the public Red/Blue observation-action interface;
2. establish random and deterministic heuristic baselines;
3. build and test the seeded configuration generator;
4. freeze training/familiar/unseen configuration splits;
5. measure simulator and baseline throughput;
6. define the reward and invalid-action treatment for the RL formulation;
7. select the smallest defensible RL algorithm and training budget;
8. run independent pilot training seeds before the main experiment.