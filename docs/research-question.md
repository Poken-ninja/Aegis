# Research Question

## Frozen question

> **Can autonomous red/blue agents learn strategies that generalize to previously unseen simulated enterprise network configurations?**

The primary research variable is **training exposure to network-configuration diversity**.

The core comparison is:

- **fixed-network training:** one network configuration during training;
- **diverse-network training:** multiple documented network configurations during training.

Both conditions are evaluated on familiar and previously unseen configurations under matched controls.

## Experimental hypotheses

### H1 — Generalization-gap hypothesis

> **Agents trained across diverse network configurations will exhibit a smaller familiar-to-unseen performance degradation than agents trained on a fixed network configuration, under the same training budget and evaluation protocol.**

H1 is evaluated separately for Red and Blue metrics.

### H2 — Unseen-performance hypothesis

> **Agents trained across diverse network configurations will achieve better performance on previously unseen network configurations than agents trained on a fixed network configuration, under the same training budget and evaluation protocol.**

H2 is also evaluated separately for Red and Blue metrics.

These are hypotheses, not expected results. The experiment may support, reject, or fail to resolve either hypothesis.

## Variables

### Primary independent variable

**Training exposure to network-configuration diversity.**

The fixed and diverse conditions should differ primarily in this variable.

### Primary dependent variables

**Red**
- attack success rate;
- actions to objective on successful attacks;
- familiar-to-unseen degradation.

**Blue**
- defense/containment success rate;
- detection time;
- familiar-to-unseen degradation.

## Metric definitions

For V1, one environment step is **one successful agent action**. Red and Blue alternate actions.

### Red attack success rate

`RED_WIN` episodes divided by valid evaluated Red episodes.

### Red actions to objective

For successful Red episodes, the number of environment actions completed through the action that first produces `RED_WIN`.

Unsuccessful episodes are not assigned an arbitrary completion time.

### Blue defense success rate

`BLUE_WIN` episodes divided by valid evaluated episodes.

For V1, `BLUE_WIN` means the simulator-defined containment condition: Blue successfully isolates Red's current non-critical host after the required detection condition.

### Blue detection time

For episodes where Blue detects the relevant compromised host, the number of environment actions completed through the Blue action that first marks that host as detected.

Detection coverage and detection time must be reported separately so episodes with no detection are not silently discarded.

### Familiar-to-unseen degradation

Raw familiar and unseen metrics are always reported.

For higher-is-better metrics:

`degradation = familiar - unseen`

For lower-is-better metrics:

`degradation = unseen - familiar`

Therefore, positive degradation consistently means worse performance on unseen configurations.

No single composite performance score is used in V1.

## Experimental controls

Unless explicitly registered as another experiment, keep constant:

- simulator/version;
- observation and action model;
- reward formulation;
- RL algorithm;
- policy architecture;
- hyperparameters;
- primary training action budget;
- episode action limit;
- configuration-generation distribution;
- training/evaluation split procedure;
- evaluation episode count and seeds;
- checkpoint-selection rule;
- opponent policy and opponent-training regime.

The exact numerical training budget is selected only after baseline and RL throughput measurements.

## Configuration splits

Before the main experiment, freeze:

1. training configurations;
2. familiar evaluation configurations;
3. unseen evaluation configurations.

The primary unseen test is a new **instance** from the same configuration family/distribution.

A secondary **unseen family/topology** test may be performed if time permits.

Unseen configurations must not influence training or checkpoint selection.

## Research contribution

AEGIS does not claim a new RL algorithm, a new simulator class, or that cyber-agent generalization itself is unexplored.

The candidate contribution is a controlled, reproducible empirical study isolating training exposure to network-configuration diversity and measuring its effect on Red and Blue policies under held-out network evaluation.

This contribution remains provisional until the final literature review.

## V1 boundary

The V1 experiment does not include:

- real-world attacks;
- real exploitation;
- malware or phishing;
- LLM-based cybersecurity;
- CTI ingestion;
- automated vulnerability discovery;
- commercial platform development;
- intelligent experience memory;
- simultaneous self-play;
- adversarial curriculum.

See `docs/research-design-freeze.md` for the complete experimental protocol and acceptance gate.
