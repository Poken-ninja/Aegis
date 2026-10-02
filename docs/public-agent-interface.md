# Public Agent Interface Contract

AEGIS agents must make decisions from public observations only.

## Red observation

Red receives:
- current position;
- discovered hosts;
- observed connections within the permitted boundary;
- roles and vulnerabilities for discovered hosts;
- current-host compromise state;
- current-host acquired privilege;
- known isolated/remediated information permitted by the model.

Red does not receive Blue hidden state or future configuration information.

## Blue observation

Blue receives:
- permitted topology and host roles;
- synthetic causal telemetry;
- prior detections;
- isolated hosts;
- remediated vulnerabilities.

Blue does not receive Red position, hidden compromise state, or hidden privilege.

## Action interface

Red actions:
- DISCOVER(target);
- MOVE(target);
- EXPLOIT(target);
- ESCALATE(target).

Blue actions:
- MONITOR();
- DETECT(target);
- ISOLATE(target);
- REMEDIATE(target).

An invalid action is a policy/environment interaction error and is recorded separately from simulator outcomes.
Unexpected simulator or configuration errors are exceptions and must not be converted into experimental outcomes.

## Testing requirement

Observation leakage tests, candidate-action tests, deterministic transition tests, invalid-action tests, and Red-to-Blue telemetry integration tests must pass before RL training.