#!/usr/bin/env bash
# Run this from the claudius/ repo root on Echelon
# Applies the Telegram → Slack migration

set -euo pipefail

echo "🏛️  Updating Claudius: Telegram → Slack"

# 1. Update requirements.txt
cat > requirements.txt << 'EOF'
pyyaml>=6.0
slack-bolt>=1.20
slack-sdk>=3.30
apscheduler>=3.10
aiosqlite>=0.20
aiohttp>=3.9
python-dotenv>=1.0
rich>=13.0
watchdog>=4.0
EOF
echo "  ✓ requirements.txt updated"

# 2. Update .env.example
cat > .env.example << 'EOF'
# Claudius Environment Variables
# Copy to .env and fill in your values

# Slack Bridge (Socket Mode — no public URL needed)
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_APP_TOKEN=xapp-your-app-level-token
SLACK_ALLOWED_USERS=U0123456789
SLACK_ALLOWED_CHANNELS=C0123456789

# Claude Code
CLAUDE_MODEL=opus
ANTHROPIC_API_KEY=  # Only if using API directly; leave blank for CLI auth

# Triune Brain SSH (uses Tailscale hostnames)
VIGIL_HOST=gx10-b71c
LUMEN_HOST=desktop-rssp6ga-1
ECHELON_HOST=avs-dellxps

# Ollama (on Vigil)
OLLAMA_ENDPOINT=http://gx10-b71c:11434

# Database (on Lumen)
POSTGRES_HOST=localhost
POSTGRES_DB=forex_agent
POSTGRES_USER=forex
POSTGRES_PASSWORD=changeme
REDIS_HOST=localhost
REDIS_PORT=6379

# Paths
FOREX_AGENT_REPO=~/forex-agent
CLAUDIUS_WORKSPACE=~/claudius
EOF
echo "  ✓ .env.example updated"

# 3. Update daemon.py — swap Telegram import for Slack
sed -i 's/bridges_config.get("telegram"/bridges_config.get("slack"/g' src/daemon.py
sed -i 's/from src.bridge.telegram import TelegramBridge/from src.bridge.slack import SlackBridge/g' src/daemon.py
sed -i 's/bridge = TelegramBridge(/bridge = SlackBridge(/g' src/daemon.py
sed -i 's/bridges\["telegram"/bridges\["slack"/g' src/daemon.py
sed -i 's/self.components\["telegram_bridge"\]/self.components["slack_bridge"]/g' src/daemon.py
sed -i 's/Telegram bridge started/Slack bridge started/g' src/daemon.py
echo "  ✓ daemon.py updated"

# 4. Update config template
cat > config/config.example.yaml << 'YAMLEOF'
# Claudius Configuration
# Copy to config.yaml and customize

claude_code:
  workspace: ~/claudius
  model: opus
  headless: true
  max_retries: 3
  session_timeout: 3600

bridges:
  slack:
    enabled: true
    bot_token: ${SLACK_BOT_TOKEN}
    app_token: ${SLACK_APP_TOKEN}
    allowed_users:
      - ${SLACK_ALLOWED_USERS}
    allowed_channels:
      - ${SLACK_ALLOWED_CHANNELS}
  telegram:
    enabled: false

scheduler:
  enabled: true
  timezone: America/New_York
  jobs:
    - name: health-check
      skill: system-health
      cron: "*/30 * * * *"
      enabled: true
    - name: daily-report
      skill: daily-report
      cron: "0 8 * * 1-5"
      enabled: true
    - name: market-prep
      skill: market-prep
      cron: "0 17 * * 0"
      enabled: false

memory:
  backend: sqlite
  db_path: memory/claudius.db
  markdown_path: memory/MEMORY.md
  max_context_tokens: 50000
  conversation_log: true
  conversation_path: memory/conversations/

skills:
  path: skills/
  auto_reload: true

triune_brain:
  enabled: true
  vigil:
    host: gx10-b71c
    ollama_port: 11434
    ssh_user: ""
  lumen:
    host: desktop-rssp6ga-1
    ssh_user: ""
  echelon:
    host: avs-dellxps
    ssh_user: ""
  forex_agent_repo: ~/forex-agent

daemon:
  pid_file: /tmp/claudius.pid
  log_level: INFO
  log_file: logs/claudius.log
  watchdog:
    enabled: true
    restart_delay: 5
    max_restarts: 10
YAMLEOF
echo "  ✓ config.example.yaml updated"

# 5. Update prompts/CLAUDIUS.md — swap Telegram refs for Slack
sed -i 's/Telegram (primary), Slack/Slack (primary), Telegram/g' prompts/CLAUDIUS.md
sed -i 's/Telegram/Slack/g' prompts/CLAUDIUS.md
echo "  ✓ CLAUDIUS.md updated"

# 6. Update README references
sed -i 's/Telegram bot (most common/Slack bot (primary/g' README.md
sed -i 's/Telegram Bot Token (for messaging bridge)/Slack Bot + App Tokens (for messaging bridge)/g' README.md
sed -i 's/Command Claudius from Telegram, Slack/Command Claudius from Slack, Telegram/g' README.md
echo "  ✓ README.md updated"

echo ""
echo "🏛️  Migration complete!"
echo ""
echo "Remaining manual steps:"
echo "  1. Review the new src/bridge/slack.py file"
echo "  2. Update .env with your Slack tokens"
echo "  3. git add -A && git commit && git push"
echo "  4. On Lumen: git pull && pip install -r requirements.txt"
