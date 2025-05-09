# === Stage 1: Builder (only for compiling if needed) ===
FROM python:3.12-slim as builder

RUN apt-get update && apt-get install -y \
    gcc \
    libncurses5-dev \
    libncursesw5-dev \
    && rm -rf /var/lib/apt/lists/*

# You can add any compile steps here if needed
# We're not installing anything here since no external libs are required

# === Stage 2: Final Runtime ===
FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    libncurses5 \
    libncursesw5 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . .

CMD ["python3", "Analyze.py"]
