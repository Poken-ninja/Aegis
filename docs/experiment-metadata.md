# Experiment Metadata Contract

Every baseline or RL run must be reproducible from recorded metadata.

Required fields:
- experiment_id
- git_commit
- training_condition (fixed or diverse, when applicable)
- configuration_ids
- configuration_seeds
- episode_seed_start or explicit episode_seeds
- algorithm
- policy_architecture
- hyperparameters
- training_action_budget
- max_episode_steps
- opponent_protocol
- checkpoint_selection
- evaluation_split
- timestamp
- notes

For baseline runs, fields that do not apply must be recorded as null rather than silently omitted.

## Reproducibility rules

1. Configuration seeds and episode seeds are recorded separately.
2. The Git commit is recorded for every measured run.
3. Fixed/diverse training conditions use the same primary action budget.
4. Evaluation configuration IDs are frozen before main training.
5. Evaluation episode seeds are frozen before main evaluation.
6. Invalid-action terminations and simulator errors are recorded separately from terminal outcomes.
7. Throughput is reported in environment actions/second so an action-count training budget can be measured.
8. A single run is never treated as sufficient evidence for the main hypothesis.

## Minimum baseline record

Before RL, a baseline record must include:
- configuration ID and seed;
- episode seeds;
- policy names;
- episode count;
- valid episode count;
- Red/Blue outcome counts;
- Red attack success rate;
- Blue defense success rate;
- successful Red actions-to-objective;
- Blue detection latency;
- invalid-action count;
- policy-error count;
- episode throughput;
- action throughput.

This contract is an engineering reproducibility requirement, not an experimental result.