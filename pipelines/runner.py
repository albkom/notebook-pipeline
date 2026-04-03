#!/usr/bin/env python3
"""Pipeline runner — reads a YAML pipeline file and runs each step in order.

Usage:
    python pipelines/runner.py pipelines/main.yaml
"""

import sys
import subprocess
from pathlib import Path

import yaml


def load_pipeline(path: str) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def run_step(step: dict, completed: set[str]) -> bool:
    name = step["name"]
    script = step["script"]
    depends_on = step.get("depends_on")

    if depends_on and depends_on not in completed:
        print(
            f"\n[PIPELINE] ERROR: step '{name}' depends on '{depends_on}'"
            f" which did not complete successfully."
        )
        return False

    print(f"\n{'=' * 60}")
    print(f"[STEP: {name}]  →  {script}")
    print("=" * 60)

    result = subprocess.run(
        [sys.executable, script],
        # stdout/stderr inherit the parent process — output streams live to the terminal
    )

    if result.returncode != 0:
        print(f"\n[PIPELINE] FAILED: '{name}' exited with code {result.returncode}")
        return False

    print(f"[PIPELINE] OK: '{name}' completed")
    return True


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python pipelines/runner.py <pipeline.yaml>")
        sys.exit(1)

    pipeline_path = sys.argv[1]

    if not Path(pipeline_path).exists():
        print(f"[PIPELINE] ERROR: pipeline file not found: {pipeline_path}")
        sys.exit(1)

    pipeline = load_pipeline(pipeline_path)
    pipeline_name = pipeline.get("name", pipeline_path)
    steps: list[dict] = pipeline.get("steps", [])

    if not steps:
        print(f"[PIPELINE] WARNING: '{pipeline_name}' has no steps defined.")
        sys.exit(0)

    print(f"[PIPELINE] Starting: {pipeline_name}  ({len(steps)} step(s))")

    completed: set[str] = set()

    for step in steps:
        ok = run_step(step, completed)
        if not ok:
            sys.exit(1)
        completed.add(step["name"])

    print(f"\n[PIPELINE] ✓ All {len(steps)} step(s) completed successfully.")


if __name__ == "__main__":
    main()
