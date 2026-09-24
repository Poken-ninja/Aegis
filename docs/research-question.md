# Research Question

## Frozen question

> Can autonomous red/blue agents learn strategies that generalize to previously unseen simulated enterprise network configurations?

## Primary independent variable

**Network configuration.**

The core comparison is:

- training on a fixed configuration;
- training across diverse configurations.

Evaluation will include both familiar configurations and configurations withheld from training.

## Experimental hypotheses

### H1 — Diverse training and generalization

Agents trained across diverse network configurations will show a smaller performance gap between familiar and previously unseen configurations than agents trained on a fixed configuration.

### H2 — Familiar versus unseen performance

Agents trained on a fixed configuration are expected to show a larger change in performance when evaluated on previously unseen configurations than when evaluated on familiar configurations.

These are hypotheses to be tested, not results. The experiment may support, reject, or fail to resolve them.

## Primary outcomes

- Red attack success rate
- Red action steps to objective
- Blue defense success rate
- Blue detection time in environment actions
- familiar vs. unseen performance
- generalization gap

### Metric definitions

For V1, one environment step is **one agent action**. Red and Blue alternate actions.

- **Red action steps to objective:** number of environment actions completed through the action that first produces `RED_WIN`.
- **Blue detection time:** number of environment actions completed through the Blue action that first marks the relevant compromised host as detected.
- **Attack success rate:** Red-win episodes divided by valid evaluated Red episodes.
- **Defense success rate:** Blue-win episodes divided by valid evaluated episodes.
- **Generalization gap:** familiar performance minus unseen performance for a specified metric, reported separately for each metric rather than collapsed into one score.

`TIMEOUT` and simulator errors are not counted as Blue wins. Simulator errors are excluded from performance denominators and reported separately.

## V1 boundary

The V1 experiment does not include:

- real-world attacks
- real exploitation
- malware or phishing
- LLM-based cybersecurity
- CTI ingestion
- automated vulnerability discovery
- commercial platform development
- intelligent experience memory
- adversarial curriculum/self-play extension

The observation model required for autonomous Red/Blue agents is a Phase 2 design dependency and must be finalized before RL training begins.