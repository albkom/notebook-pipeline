"""Step two — reads step_one output and prints a summary to stdout.

Replace this logic with your own notebook-converted code.
Environment variables (set in .env):
    OUTPUT_DIR — directory where step_one wrote its output
"""

import csv
import os
from pathlib import Path

OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "data/output"))
INPUT_FILE = OUTPUT_DIR / "step_one_output.csv"


def summarize(rows: list[dict]) -> None:
    if not rows:
        print("[step_two] No rows to summarize.")
        return

    print(f"\n[step_two] Summary — {len(rows)} row(s)")
    print("-" * 40)

    for col in rows[0].keys():
        values = []
        for row in rows:
            try:
                values.append(float(row[col]))
            except (ValueError, TypeError):
                break
        else:
            if values:
                total = sum(values)
                print(
                    f"  {col:12s}  count={len(values)}"
                    f"  sum={total:.2f}"
                    f"  avg={total / len(values):.2f}"
                    f"  min={min(values):.2f}"
                    f"  max={max(values):.2f}"
                )
                continue
        # Non-numeric column: show unique values
        unique = sorted({row[col] for row in rows})
        print(f"  {col:12s}  unique values: {unique}")

    print("-" * 40)


def main() -> None:
    if not INPUT_FILE.exists():
        print(f"[step_two] ERROR: expected input not found: {INPUT_FILE}")
        raise SystemExit(1)

    with open(INPUT_FILE, newline="") as f:
        rows = list(csv.DictReader(f))

    print(f"[step_two] Loaded {len(rows)} row(s) from {INPUT_FILE}")
    summarize(rows)
    print("[step_two] Done.")


if __name__ == "__main__":
    main()
