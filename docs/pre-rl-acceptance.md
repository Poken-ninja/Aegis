# Pre-RL Acceptance Checklist

Status: engineering implementation complete; final local verification required before RL.

1. **Invalid-action exception boundary** — explicit `InvalidActionError`; simulator/configuration errors remain exceptions.
2. **Runner classification tests** — invalid actions are recorded separately; simulator errors are not misclassified.
3. **Public observation/action contract** — documented and covered by leakage/candidate tests.
4. **Red-to-Blue telemetry integration** — escalation telemetry is visible to the next Blue observation.
5. **Blue containment regression** — heuristic Blue isolates only when its observable evidence justifies containment.
6. **Detection metric semantics** — detection latency starts at first observable telemetry for the detected host; compromise is not required.
7. **Throughput measurement** — baselines report environment actions/second for action-budget sizing.
8. **Seeded configuration generator** — deterministic topology/connectivity variation under a configuration seed.
9. **Reproducible configuration splits** — train/familiar/unseen records are deterministic and disjoint.
10. **Multi-seed baseline sanity** — heuristic behavior is exercised across generated configurations and multiple episode seeds.
11. **Experiment metadata contract** — required provenance, seeds, budget, opponent, and evaluation fields are defined.
12. **Research-design/literature alignment** — current literature is reflected in the contribution boundary; no unsupported novelty claim.

## Gate condition

Do not begin RL training until the local full test suite passes after pulling this branch and the baseline sanity commands produce valid, reproducible records.

Passing tests are engineering evidence only. They do not establish H1/H2 or generalization performance.