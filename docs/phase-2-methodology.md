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

The current local simulator/observation test suite reports:

- **116 tests collected**
- **116 tests passed**

This is an engineering validation result only. It is not an RL result and does not establish generalization.

No PPO, MARL, DGX training, or generalization performance result has been produced yet.

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
1. complete the public Red/Blue observation-action interface;
2. test it through the public boundary;
3. establish simple random and deterministic heuristic baselines;
4. measure simulator throughput;
5. then select the smallest defensible RL configuration.