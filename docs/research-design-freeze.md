# Research Design Freeze — AEGIS V1

**Status:** Proposed freeze for review and implementation  
**Date:** 2026-09-30  
**Branch:** `phase-2/controlled-learning-methodology`

This document is the single methodological reference for the V1 research experiment. Engineering decisions must support this design unless an explicit decision record changes it.

## 1. Research question

> **Can autonomous red/blue agents learn strategies that generalize to previously unseen simulated enterprise network configurations?**

The project studies whether exposure to **network-configuration diversity during training** changes how learned Red and Blue policies behave on configurations not used for training.

This is a simulation study. It does not claim real-world attack or defense effectiveness.

## 2. Research contribution — carefully scoped

AEGIS does **not** claim a new RL algorithm, a new cybersecurity simulator class, or that generalization to novel cyber scenarios is itself novel.

Existing work already demonstrates:
- abstract simulated enterprise-network RL with Red/Blue interaction (CyberBattleSim);
- training offensive agents and transfer/generalization to novel scenarios (NASimEmu);
- RL defensive policies and generalization across attacker strategies (graph-based cyber-attack simulation work);
- automated offensive and defensive agents in attack/defense simulation environments (recent MAL Simulator work).

Therefore, the **candidate contribution** for AEGIS is narrower:

> A reproducible undergraduate empirical study that isolates **training exposure to network-configuration diversity** as the primary manipulated factor and measures its effect on Red and Blue policy performance on familiar versus held-out simulated enterprise configurations, using an explicit observation boundary and controlled opponents.

This is a **candidate contribution, not a novelty claim**. The final report must describe it as such unless a broader literature review establishes a stronger gap.

## 3. Hypotheses

### H1 — Generalization-gap hypothesis

> **Agents trained across diverse network configurations will exhibit a smaller familiar-to-unseen performance degradation than agents trained on a fixed network configuration, under the same training budget and evaluation protocol.**

H1 is tested separately for Red and Blue metrics. It does not assume that either condition will perform well in absolute terms.

### H2 — Unseen-performance hypothesis

> **Agents trained across diverse network configurations will achieve better performance on previously unseen network configurations than agents trained on a fixed network configuration, under the same training budget and evaluation protocol.**

H2 is also evaluated separately for Red and Blue metrics.

Both hypotheses may be supported, rejected, or unresolved.

## 4. Variables

### Primary independent variable

**Training exposure to network-configuration diversity**

- **Fixed condition:** training uses one fixed network configuration.
- **Diverse condition:** training samples from a documented set/distribution of multiple configurations.

### Primary dependent variables

Red:
1. attack success rate;
2. actions to objective among successful attacks;
3. familiar-to-unseen degradation.

Blue:
1. defense/containment success rate;
2. detection time;
3. familiar-to-unseen degradation.

### Controlled variables

Unless explicitly registered as an additional experiment:
- simulator rules/version;
- action vocabulary;
- observation model;
- reward formulation;
- RL algorithm;
- policy architecture;
- hyperparameters;
- primary training budget;
- episode action limit;
- configuration-generation distribution;
- training/evaluation split procedure;
- number of evaluation episodes;
- evaluation seeds;
- opponent policy and opponent-training regime;
- checkpoint-selection rule.

## 5. Metric definitions

One environment step is one successful agent action. Red and Blue alternate actions.

### Red attack success rate

[
ASR = \frac{N(RED\_WIN)}{N(valid\ Red\ evaluation\ episodes)}
]

Simulator errors and invalid-policy terminations are reported separately and do not become Red wins/losses by convention.

### Red actions to objective

For successful Red episodes:

> number of environment actions completed through the action that first produces `RED_WIN`.

Report successful episodes separately from unsuccessful episodes; do not hide failures by assigning them an arbitrary step count.

### Blue defense success rate

[
DSR = \frac{N(BLUE\_WIN)}{N(valid\ evaluation\ episodes)}
]

For V1, `BLUE_WIN` means the simulator-defined containment condition: Blue successfully isolates Red's current non-critical host after the required detection condition.

This is not a claim of general real-world prevention effectiveness.

### Blue detection time

For episodes where Blue detects the relevant compromised host:

> number of environment actions completed through the Blue action that first marks that host as detected.

Detection time is undefined for episodes where the relevant host is never detected; those episodes remain represented in detection-rate reporting rather than being silently discarded from all analyses.

### Familiar-to-unseen degradation

For each metric, report familiar and unseen values separately.

Do **not** create a single composite score.

Because some metrics are higher-is-better and others are lower-is-better, the report will use a normalized degradation convention:

- for higher-is-better metrics (attack success, defense success):

[
D = M_{familiar} - M_{unseen}
]

- for lower-is-better metrics (steps to objective, detection time):

[
D = M_{unseen} - M_{familiar}
]

Positive (D) therefore consistently means **worse performance on unseen configurations**.

The generalization analysis must still show the raw familiar and unseen metrics.

## 6. Experimental conditions

### Training condition A — Fixed

The policy trains on one configuration (C_f).

The configuration remains fixed across training episodes.

### Training condition B — Diverse

The policy trains across multiple configurations sampled from the predefined training configuration set/distribution.

### Equal-budget rule

Both conditions receive the same primary training budget, preferably measured in **environment actions**, because one simulator step corresponds to one agent action.

The numeric budget will be selected only after baseline and RL throughput are measured. It must be frozen before the main experiment.

## 7. Evaluation design

Before training begins, freeze:

- training configuration IDs/seeds;
- familiar evaluation configuration IDs/seeds;
- unseen evaluation configuration IDs/seeds;
- evaluation episode seeds;
- opponent policies;
- checkpoint-selection rule.

### Familiar evaluation

Configurations from the same training exposure/distribution that were not used for the training updates being evaluated.

### Primary unseen evaluation

New **instances** withheld from training.

The primary claim is instance-level generalization.

### Secondary unseen evaluation

If time permits, evaluate on an unseen **configuration/topology family**.

This is stronger structural generalization, but it is secondary because it increases experimental complexity.

## 8. Opponent protocol

The core experiment uses **controlled opponents**, not simultaneous Red/Blue learning.

For Red evaluation:
- evaluate the learned Red policy against a fixed documented Blue baseline.

For Blue evaluation:
- evaluate the learned Blue policy against a fixed documented Red baseline.

The exact baseline policy will be selected after the random and heuristic baseline study.

Opponent strength must remain constant across fixed-versus-diverse comparisons.

Simultaneous learned Red-vs-Blue co-adaptation is deferred to an optional extension and is not part of the primary hypothesis test.

## 9. Configuration-generation requirements

Every generated network configuration must have:

- configuration ID;
- configuration seed;
- reproducible generation parameters;
- topology/connectivity;
- host roles;
- vulnerability placement;
- privilege requirements;
- segmentation/connectivity properties used by the generator;
- critical-asset placement.

Configuration randomness must be separated from episode randomness.

A configuration must not change merely because an episode seed changes.

## 10. Simulator assumptions that are frozen for V1

The simulator is a synthetic cyber environment, not an emulator of real systems.

### Network
- graph-based synthetic hosts and connections;
- small enterprise topology;
- configuration variation is the research variable.

### Red
- DISCOVER;
- MOVE;
- EXPLOIT;
- ESCALATE.

Discovery does not equal compromise.

Internal movement requires an appropriate compromised foothold; Internet-to-Web initial entry is an explicit exception.

Synthetic privilege is:

[
NONE \rightarrow USER \rightarrow ADMIN
]

The retained highest privilege is a deliberately simplified attacker capability abstraction, not a model of real credential/session behavior.

### Blue
- MONITOR;
- DETECT;
- ISOLATE;
- REMEDIATE.

Blue receives synthetic causal telemetry rather than hidden compromise state.

Detection means identifying observable suspicious activity; it is not equivalent to proving compromise.

Containment/remediation operate on the stronger detected-compromise condition.

### Outcomes
- `RED_WIN`: critical asset compromised;
- `BLUE_WIN`: V1 containment condition achieved;
- `TIMEOUT`: action budget exhausted without a win;
- simulator/configuration errors: exceptions, not experimental outcomes.

### Randomness
- configuration seed controls network generation;
- episode seed controls stochastic episode events;
- both are recorded.

## 11. Observation boundary

Red may observe only information defined by the Red observation model.

Blue may observe:
- permitted topology/roles;
- synthetic telemetry;
- prior detections;
- isolated hosts;
- remediated vulnerabilities.

Blue must not receive:
- Red's hidden position;
- `compromised_hosts`;
- Red's hidden privilege;
- other simulator ground truth that bypasses evidence-based detection.

Observation leakage is an experimental-validity failure, not merely a software bug.

## 12. Baselines before RL

Before selecting or training a complex RL policy, establish:

1. random policy;
2. simple deterministic Red heuristic;
3. simple deterministic Blue heuristic.

Measure:
- valid-action rate;
- invalid-action rate;
- outcome distribution;
- trajectory length;
- Red/Blue primary metrics;
- simulator throughput.

These baselines serve two purposes:
- establish that the simulator produces interpretable behavior;
- provide non-learning reference points for later RL results.

## 13. RL policy selection

PPO remains a candidate, not a commitment.

Algorithm selection occurs after:
1. public observation/action interface validation;
2. baseline behavior validation;
3. throughput measurement;
4. action/observation encoding review.

The smallest defensible RL formulation will be chosen.

The experiment is about **generalization from network diversity**, not about proving one RL algorithm is superior.

## 14. Statistical/reproducibility plan

The main experiment must use multiple independent training seeds.

The exact number will be selected after throughput measurement and time-budget review.

For every run record:
- code version/commit;
- configuration IDs/seeds;
- episode seeds;
- training condition;
- algorithm and hyperparameters;
- training action budget;
- checkpoint-selection result;
- evaluation results;
- invalid-action counts;
- simulator errors;
- runtime/throughput where relevant.

Report uncertainty across independent runs rather than presenting one seed as definitive evidence.

If the project cannot afford enough independent runs for a strong statistical claim, the final report must explicitly describe the result as preliminary.

## 15. What would count as evidence

### Supporting H1
The diverse condition shows a smaller familiar-to-unseen degradation than the fixed condition, consistently across independent runs and relevant metrics.

### Supporting H2
The diverse condition shows higher unseen performance for higher-is-better metrics and/or lower unseen cost/time for lower-is-better metrics, under matched controls.

### Rejecting or failing to resolve
Results may show:
- no meaningful difference;
- fixed training performing similarly;
- diverse training helping some metrics but not others;
- high variance preventing a clear conclusion.

All are valid research outcomes.

## 16. What is NOT evidence

The following do not answer the research question:
- passing simulator tests;
- faster GPU training;
- higher training reward alone;
- performance on training configurations only;
- one successful demo;
- one random seed;
- a model checkpoint without held-out evaluation.

## 17. Scope freeze

Not part of the core experiment:
- real-world attacks;
- real exploitation;
- malware/phishing;
- LLM cybersecurity;
- CTI ingestion;
- automated vulnerability discovery;
- large knowledge graphs;
- commercial platform development;
- advanced agent memory;
- simultaneous self-play;
- adversarial curriculum;
- large distributed infrastructure.

If the schedule slips, remove secondary experiments before weakening the core fixed-versus-diverse comparison.

## 18. Acceptance gate before RL

RL training does not begin until:

- research question and hypotheses are frozen;
- metrics and directionality are frozen;
- simulator semantics are reconciled;
- public observation/action interface is tested;
- information leakage tests pass;
- random and heuristic baselines run successfully;
- configuration generator is deterministic under seed;
- training/familiar/unseen split procedure is reproducible;
- opponent protocol is defined;
- training budget is measurable;
- experiment metadata format is defined.

## 19. Literature-grounding note

The design deliberately does not claim that autonomous cyber-agent generalization is unexplored.

CyberBattleSim already demonstrated abstract Red/Blue interaction in a simulated enterprise environment and highlighted the importance of network topology/configuration to lateral movement. NASimEmu explicitly studied agents transferring to novel scenarios. Other work has studied RL defenders, attacker/defender simulation, and generalization across attacker strategies.

AEGIS therefore treats **controlled training-diversity comparison under held-out network configurations** as the experimental focus, while keeping the contribution claim provisional until the final literature review.

## 20. References checked for this freeze

- Microsoft CyberBattleSim / Microsoft Research and Security Blog.
- Janisch, Pevný, and Lisý, *NASimEmu: Network Attack Simulator & Emulator for Training Agents Generalizing to Novel Scenarios* (2023).
- Nyberg and Johnson, *Training Automated Defense Strategies Using Graph-based Cyber Attack Simulations* (2023).
- Hammar and Stadler, *Learning Near-Optimal Intrusion Responses Against Dynamic Attackers* (2023).
- Nyberg et al., *The MAL Simulator: Cyber Operations Simulation based on Attack & Defense Graphs* (2026).
- Wang et al., *CyberGym* and *CyberGym-E2E* (2025–2026), which concern LLM/AI-agent cybersecurity evaluation rather than the core AEGIS RL experiment.

These references are used to constrain the contribution claim, not to imply that AEGIS has reproduced or surpassed those systems.
