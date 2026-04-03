"""Step one — reads CSV files from INPUT_DIR and writes a merged output to OUTPUT_DIR.

Replace this logic with your own notebook-converted code.
Environment variables (set in .env):
    INPUT_DIR  — directory to read source files from
    OUTPUT_DIR — directory to write results to
"""

import csv
import os
from pathlib import Path

INPUT_DIR = Path(os.getenv("INPUT_DIR", "data/input"))
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "data/output"))
OUTPUT_FILE = OUTPUT_DIR / "step_one_output.csv"

SAMPLE_ROWS = [
    {"id": "1", "value": "10", "label": "alpha"},
    {"id": "2", "value": "25", "label": "beta"},
    {"id": "3", "value": "7",  "label": "alpha"},
    {"id": "4", "value": "42", "label": "gamma"},
    {"id": "5", "value": "15", "label": "beta"},
]


def main() -> None:
    csv_files = sorted(INPUT_DIR.glob("*.csv"))

    if csv_files:
        rows: list[dict] = []
        for path in csv_files:
            print(f"[step_one] Reading {path}")
            with open(path, newline="") as f:
                rows.extend(list(csv.DictReader(f)))
        print(f"[step_one] Loaded {len(rows)} row(s) from {len(csv_files)} file(s)")
    else:
        print(f"[step_one] No CSV files found in {INPUT_DIR} — using built-in sample data")
        rows = SAMPLE_ROWS

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print(f"[step_one] Output written → {OUTPUT_FILE}  ({len(rows)} row(s))")


if __name__ == "__main__":
    main()
