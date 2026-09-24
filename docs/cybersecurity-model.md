# Cybersecurity Model

AEGIS is a synthetic cyber-range. Its purpose is to model cybersecurity decisions and consequences in a controlled environment, not to reproduce real infrastructure or provide operational attack tooling.

## Network

A network is a graph:

- node = synthetic host
- edge = simulated network connection

The initial reference network contains:

```text
Internet
    |
   Web
    |
   App
  /   \\
Work   DB
        |
     Critical
```

## Red

Red represents a simulated attacker.

Initial action vocabulary:

- DISCOVER
- MOVE
- EXPLOIT
- ESCALATE

These are simulator state transitions. They do not execute real exploits.

## Blue

Blue represents a simulated defender.

Initial action vocabulary:

- MONITOR
- DETECT
- ISOLATE
- REMEDIATE

These are abstract defensive capabilities with simulator-defined consequences.

**Phase-1 limitation:** `MONITOR` is currently a no-op and `DETECT` is a low-level state-transition primitive that can mark an already-compromised host as detected. This does **not** define the eventual autonomous Blue observation interface.

Before RL training, Blue must receive an explicit observation model that does not expose the hidden `compromised_hosts` state directly. The observation model is a Phase 2 design requirement.

## Outcomes

### RED_WIN

Red compromises the critical asset.

### BLUE_WIN

For V1, Blue wins only when it successfully contains Red by isolating Red's current non-critical host. This is intentionally narrower than a general claim of prevention.

### TIMEOUT

The episode reaches its action-step limit without either win condition.

### Simulator error

Invalid actions and invalid network configurations are simulator exceptions, not experimental episode outcomes. They are not counted as Red or Blue performance.

## Cyber-state semantics

The simulator distinguishes:

- `discovered_hosts`: hosts Red has discovered;
- `red_position`: Red's current location;
- `compromised_hosts`: hosts Red has successfully compromised;
- `host_privileges`: where Red acquired synthetic privilege;
- `detected_hosts`: compromised hosts Blue has marked as detected;
- `isolated_hosts`: hosts Blue has contained;
- `remediated_vulnerabilities`: vulnerabilities disabled by Blue.

For V1, Red retains its highest acquired synthetic privilege as an attacker capability across the episode. This is a deliberate abstraction and not a model of real credential/session behavior.

## Time semantics

One simulator `step` is one successful agent action. Red and Blue alternate actions.

Therefore:

- `step_count` counts individual successful agent actions;
- `max_steps` is an action budget;
- terminal metrics can use `step_count` directly without interpreting it as completed Red/Blue rounds.

## Research-model boundary

The simulator state is the hidden ground-truth state. Agent observations are a separate layer and must be defined before RL.

This separation is important because autonomous defense research requires a distinction between:

1. true network/cyber state;
2. what an agent can observe;
3. what an agent can act upon;
4. the resulting state transition;
5. the episode outcome.

The V1 simulator is intentionally small enough that these concepts can be tested independently.

## Safety

All offensive behavior remains synthetic, non-operational, and confined to the simulator.