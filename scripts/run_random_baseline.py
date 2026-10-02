"""Run the reproducible Random Red versus Random Blue baseline."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict

from aegis.baselines import run_random_baseline


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes", type=int, default=100)
    parser.add_argument("--configuration-seed", type=int, default=0)
    parser.add_argument("--episode-seed-start", type=int, default=0)
    parser.add_argument("--max-steps", type=int, default=50)
    args = parser.parse_args()

    summary = run_random_baseline(
        episode_count=args.episodes,
        configuration_seed=args.configuration_seed,
        episode_seed_start=args.episode_seed_start,
        max_steps=args.max_steps,
    )

    print(json.dumps(asdict(summary), indent=2))


if __name__ == "__main__":
    main()
