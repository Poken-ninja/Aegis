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

### Current status

Phase 1 is not yet accepted.

The next engineering work is to reconcile the network model, cyber state, environment rules, tests, and decision documentation before adding RL.

### Rule for reporting results

No learning performance, generalization result, attack success rate, or defense success rate will be reported until the corresponding experiment has actually been executed.

Failed tests and negative results will be retained as part of the research record.
