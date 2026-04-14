FROM python:3.11-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    openssh-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Claude Code CLI
RUN curl -fsSL https://claude.ai/install.sh | sh || true

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create runtime directories
RUN mkdir -p memory/conversations logs

# Non-root user
RUN useradd -m claudius && chown -R claudius:claudius /app
USER claudius

# SSH config directory
RUN mkdir -p ~/.ssh && chmod 700 ~/.ssh

ENTRYPOINT ["python", "-m", "src.daemon"]
