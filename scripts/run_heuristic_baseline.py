"""Run the deterministic heuristic baseline."""

import argparse
import json
from dataclasses import asdict

from aegis.baselines import run_heuristic_baseline


parser = argparse.ArgumentParser()
parser.add_argument("--episodes", type=int, default=100)
args = parser.parse_args()

summary = run_heuristic_baseline(episode_count=args.episodes)
print(json.dumps(asdict(summary), indent=2))
