import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # env vars already set (e.g. inside Docker via env_file)

OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "data/output"))
INPUT_FILE = OUTPUT_DIR / "step_one_output.csv"

SMTP_HOST     = os.getenv("SMTP_HOST", "mailhog")
SMTP_PORT     = int(os.getenv("SMTP_PORT", "1025"))
SMTP_USER     = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
EMAIL_FROM    = os.getenv("EMAIL_FROM", "pipeline@example.com")
EMAIL_TO      = os.getenv("EMAIL_TO", "recipient@example.com")

print(f"Input file : {INPUT_FILE}")
print(f"SMTP       : {SMTP_HOST}:{SMTP_PORT}")
print(f"From       : {EMAIL_FROM}")
print(f"To         : {EMAIL_TO}")

import csv

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"Input file not found: {INPUT_FILE}\n"
        "Run step_one (and step_two) before executing this notebook."
    )

with open(INPUT_FILE, newline="") as f:
    rows = list(csv.DictReader(f))

print(f"Loaded {len(rows)} row(s) from {INPUT_FILE}")
print(f"Columns: {list(rows[0].keys()) if rows else '(none)'}")

def _summary_stats(rows: list[dict]) -> str:
    """Return an HTML <ul> with per-column statistics."""
    if not rows:
        return "<ul><li>No data.</li></ul>"
    items = []
    for col in rows[0].keys():
        values = []
        for row in rows:
            try:
                values.append(float(row[col]))
            except (ValueError, TypeError):
                break
        else:
            if values:
                items.append(
                    f"<li><b>{col}</b>: count={len(values)}, "
                    f"sum={sum(values):.2f}, avg={sum(values)/len(values):.2f}, "
                    f"min={min(values):.2f}, max={max(values):.2f}</li>"
                )
                continue
        unique = ", ".join(sorted({row[col] for row in rows}))
        items.append(f"<li><b>{col}</b>: {unique}</li>")
    return "<ul>" + "".join(items) + "</ul>"


def build_html_report(rows: list[dict]) -> str:
    if not rows:
        return "<html><body><p>No data available.</p></body></html>"

    columns = list(rows[0].keys())

    header = "<tr>" + "".join(f"<th>{c}</th>" for c in columns) + "</tr>"
    body   = "".join(
        "<tr>" + "".join(f"<td>{row.get(c, '')}</td>" for c in columns) + "</tr>"
        for row in rows
    )

    return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body  {{ font-family: Arial, sans-serif; font-size: 14px; color: #333; }}
    h2    {{ color: #0057b8; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th    {{ background: #0057b8; color: #fff; padding: 8px 12px; text-align: left; }}
    td    {{ padding: 6px 12px; border-bottom: 1px solid #ddd; }}
    tr:nth-child(even) td {{ background: #f5f9ff; }}
  </style>
</head>
<body>
  <h2>Pipeline Report</h2>
  <p>Generated on <b>{__import__('datetime').date.today()}</b> — {len(rows)} row(s) from <code>{INPUT_FILE.name}</code>.</p>
  <h3>Data</h3>
  <table>{header}{body}</table>
  <h3>Summary</h3>
  {_summary_stats(rows)}
</body>
</html>"""


html_body = build_html_report(rows)
print(f"Report built — {len(html_body):,} characters.")

import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

recipients = [addr.strip() for addr in EMAIL_TO.split(",") if addr.strip()]

msg = MIMEMultipart("alternative")
msg["Subject"] = "Pipeline Report"
msg["From"]    = EMAIL_FROM
msg["To"]      = ", ".join(recipients)
msg.attach(MIMEText(html_body, "html", "utf-8"))

context = ssl.create_default_context()

if SMTP_PORT == 465:
    # Implicit TLS (SMTPS)
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=context) as server:
        if SMTP_USER:
            server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(EMAIL_FROM, recipients, msg.as_string())
else:
    # Explicit TLS via STARTTLS (port 587) or plain (port 25)
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.ehlo()
        if SMTP_PORT != 25:
            server.starttls(context=context)
            server.ehlo()
        if SMTP_USER:
            server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(EMAIL_FROM, recipients, msg.as_string())

print(f"Email sent successfully to: {', '.join(recipients)}")
