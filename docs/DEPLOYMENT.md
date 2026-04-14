# Deployment Guide

## Deploying Claudius on Lumen

### Prerequisites
1. Claude Code CLI installed and authenticated on Lumen
2. Docker installed on Lumen
3. Tailscale running with connectivity to Vigil and Echelon
4. Telegram bot created via @BotFather (if using Telegram bridge)

### Step 1: Clone and Configure
```bash
cd ~
git clone https://github.com/vonstegen/claudius.git
cd claudius
cp .env.example .env
cp config/config.example.yaml config/config.yaml
# Edit .env and config/config.yaml with your values
```

### Step 2: Test Locally
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m src.daemon
```
Send a test message via Telegram. If it responds, you're ready to containerize.

### Step 3: Deploy with Docker
```bash
docker compose up -d
docker logs -f claudius  # Watch startup
```

### Step 4: Verify
- Send `/start` to your Telegram bot
- Send "check health" to trigger the system-health skill
- Check logs: `docker logs claudius --tail 50`

### Auto-start on Boot
Docker's `restart: unless-stopped` handles this. Verify with:
```bash
sudo reboot
# After reboot:
docker ps | grep claudius
```

### Updating
```bash
cd ~/claudius
git pull
docker compose down
docker compose up -d --build
```
