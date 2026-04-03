# scripting-python

A lightweight Python pipeline environment. Write code in Jupyter notebooks, convert to `.py` scripts, compose them into pipelines, and run everything in Docker.

---

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
- VS Code (optional, but tasks are pre-configured)

---

## Quick start

```bash
# 1. Copy the example env file and fill in your values
cp .env.example .env

# 2. Start all services (includes Mailhog for local email testing)
docker compose up -d

# 3. Run the default pipeline
docker compose run --rm python python pipelines/runner.py pipelines/main.yaml
```

You'll see per-step output streamed to your terminal:

```
[PIPELINE] Starting: main  (3 step(s))

============================================================
[STEP: step_one]  →  scripts/step_one.py
============================================================
[step_one] No CSV files found in data/input — using built-in sample data
[step_one] Output written → data/output/step_one_output.csv  (5 row(s))
[PIPELINE] OK: 'step_one' completed

============================================================
[STEP: step_two]  →  scripts/step_two.py
============================================================
[step_two] Loaded 5 row(s) from data/output/step_one_output.csv
...
[PIPELINE] OK: 'step_two' completed

============================================================
[STEP: step_three]  →  scripts/send_email_report.py
============================================================
Email sent successfully to: recipient@example.com
[PIPELINE] ✓ All 3 step(s) completed successfully.
```

---

## VS Code tasks

Open the Command Palette → **Tasks: Run Task** (or `Ctrl+Shift+B` for the default):

| Task | Description |
|---|---|
| **Pipeline: Run** | Builds image if needed, then runs `pipelines/main.yaml` |
| **Docker: Build** | Rebuilds the image (run after editing `requirements.txt`) |
| **Notebook: Convert → Script** | Prompts for a `.ipynb` filename in `notebooks/`, converts it to a `.py` file in `scripts/` |

---

## Email reporting (Mailhog)

The pipeline includes a `notebooks/send_email_report.ipynb` notebook that reads data produced by earlier steps and sends an HTML summary email.

During local development, emails are captured by **Mailhog** — no real emails are sent.

| Service | URL |
|---|---|
| Mailhog web UI | http://localhost:8025 |
| SMTP (internal) | `mailhog:1025` |

Configure these variables in `.env` (see `.env.example`):

| Variable | Description |
|---|---|
| `SMTP_HOST` | `mailhog` for local dev, or your real SMTP host |
| `SMTP_PORT` | `1025` for Mailhog, `587` for STARTTLS, `465` for SSL |
| `SMTP_USER` | SMTP login (leave blank for Mailhog) |
| `SMTP_PASSWORD` | SMTP password (leave blank for Mailhog) |
| `EMAIL_FROM` | Sender address |
| `EMAIL_TO` | Recipient(s), comma-separated |

To add this as a pipeline step, convert the notebook to a script then register it in `pipelines/main.yaml`:

```bash
docker compose run --rm python jupyter nbconvert --to script notebooks/send_email_report.ipynb --output-dir scripts/
```

```yaml
# pipelines/main.yaml
steps:
  - name: step_three
    script: scripts/send_email_report.py
    depends_on: step_two
```

---

## Adding a new pipeline step

**Step 1** — Write code in a notebook, save it to `notebooks/my_analysis.ipynb`.

**Step 2** — Convert it to a script (VS Code task or CLI):

```bash
docker compose run --rm python jupyter nbconvert --to script notebooks/my_analysis.ipynb --output-dir scripts/
```

**Step 3** — Register the step in `pipelines/main.yaml`:

```yaml
steps:
  - name: my_analysis
    script: scripts/my_analysis.py
    depends_on: step_two   # optional: name of the step that must succeed first
```

**Step 4** — Run the pipeline. Done.

---

## Passing data between steps

Steps communicate via files in `data/`. Read env vars to get the correct paths:

```python
import os
from pathlib import Path

INPUT_DIR  = Path(os.getenv("INPUT_DIR",  "data/input"))
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "data/output"))
```

| Directory | Purpose |
|---|---|
| `data/input/` | Drop source files here before running |
| `data/output/` | Steps write results here; gitignored |

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│  Your machine                                       │
│                                                     │
│  VS Code (IntelliSense, tasks)                      │
│  notebooks/  →  nbconvert  →  scripts/              │
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │  Docker (docker compose up)                  │   │
│  │                                             │   │
│  │  python:3.12-slim container                 │   │
│  │    pipelines/runner.py                      │   │
│  │      reads main.yaml                        │   │
│  │      spawns subprocess per step             │   │
│  │      streams stdout to your terminal        │   │
│  │      exits on first failure                 │   │
│  │                                             │   │
│  │    scripts/step_one.py  ──┐                 │   │
│  │    scripts/step_two.py  ←─┘  data/output/   │   │
│  │    scripts/send_email_report.py             │   │
│  │        │                                   │   │
│  │        ▼                                   │   │
│  │  mailhog container  (SMTP :1025)            │   │
│  │    web UI → http://localhost:8025           │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
│  Volume mounts:  .  →  /app                         │
└─────────────────────────────────────────────────────┘
```

### Key decisions

**Notebooks are dev artifacts, `.py` files are the pipeline artifact.**  
`nbconvert` is the bridge. You keep the notebook for exploration; the script is what the pipeline runs.

**Steps communicate via files, not in-memory objects.**  
Each step runs as its own subprocess, so there is no shared memory. Files in `data/output/` are the contract between steps — easy to inspect, easy to re-run from any point.

**Pipeline definition is a YAML file.**  
`pipelines/main.yaml` is the single source of truth for step order and dependencies. Add new pipelines by adding new YAML files and pointing the runner at them.

**No orchestration framework.**  
`runner.py` is ~60 lines of plain Python. It covers linear pipelines with optional `depends_on` guards. If you later need a full DAG, parallel execution, or a UI, that is the moment to evaluate [Prefect](https://www.prefect.io/) or [Ploomber](https://ploomber.io/).

---

## Adding Python dependencies

1. Add the package to `requirements.txt`
2. Rebuild the image: `docker compose build`

For IntelliSense on the host, create a local venv and install the same requirements:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

VS Code will pick up the venv automatically (select it as the Python interpreter if prompted).
