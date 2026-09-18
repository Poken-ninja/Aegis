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
  /   \
Work   DB
        |
     Critical
```

## Red

Red represents a simulated attacker.

Initial action vocabulary:

- SCAN
- DISCOVER
- EXPLOIT
- MOVE
- ESCALATE

These are simulator state transitions. They do not execute real exploits.

## Blue

Blue represents a simulated defender.

Initial action vocabulary:

- MONITOR
- DETECT
- BLOCK
- ISOLATE
- PATCH

These are abstract defensive capabilities with simulator-defined consequences.

## Outcomes

### RED_WIN

Red compromises the critical asset.

### BLUE_WIN

Blue successfully suppresses, contains, or prevents Red from reaching its objective according to explicit simulator rules.

### TIMEOUT

The episode reaches its step limit without either win condition.

### ERROR

The simulator itself fails or receives an invalid operation that cannot be handled as a defined simulation event.

An ERROR is never counted as Red or Blue performance.

## Important modeling principle

The simulator must distinguish:

1. network structure,
2. cyber state,
3. agent observations,
4. agent actions,
5. state transitions,
6. episode outcomes.

This separation allows us to test the cybersecurity model before adding reinforcement learning.
