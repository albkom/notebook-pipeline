FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Source is mounted as a volume during development — no COPY needed.
# For production builds, uncomment the line below:
# COPY . .
