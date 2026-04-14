# Claudius

**An autonomous AI companion built on Claude Code — OpenClaw-style superpowers without the downsides.**

Claudius is a standalone, self-hosted AI agent system that wraps Claude Code in a persistent daemon with messaging bridges, proactive scheduling, markdown-based skills, persistent memory, and multi-agent delegation. It runs on your hardware, uses your Claude Max subscription, and stays fully under your control.

## What Claudius Does

- **Always-on daemon** — Runs 24/7 on a dedicated machine (Lumen), auto-restarts on crash
- **Messaging bridge** — Command Claudius from Slack, Telegram, or Discord from anywhere
- **Proactive heartbeat** — Cron-based scheduling for recurring tasks (inbox triage, system health checks, daily reports)
- **Skills system** — Markdown playbooks in `skills/` that Claudius follows natively
- **Persistent memory** — File-based + SQLite memory that survives restarts and sessions
- **Multi-agent delegation** — Manager → specialist sub-agent patterns via Claude Code's native Agent Teams
- **Secure by design** — Runs in Docker, minimal permissions, no broad desktop access

## Architecture

```
┌─────────────────────────────────────────────┐
│  Claudius Daemon (Python)                   │
│  ├── Messaging Bridge (Telegram/Slack)      │
│  ├── Heartbeat Scheduler (cron)             │
│  ├── Task Router                            │
│  └── Session Manager                        │
├─────────────────────────────────────────────┤
│  Claude Code CLI (headless, -p mode)        │
│  ├── CLAUDIUS.md (system prompt)            │
│  ├── MEMORY.md (persistent context)         │
│  └── skills/ (markdown playbooks)           │
├─────────────────────────────────────────────┤
│  Storage Layer                              │
│  ├── SQLite (conversations, tasks, state)   │
│  ├── File-based memory (markdown)           │
│  └── Vector store (optional, for RAG)       │
└─────────────────────────────────────────────┘
```

## Primary Use Case: Triune Brain R&D Companion

Claudius was designed as the external architect for the [forex-agent](https://github.com/vonstegen/forex-agent) Triune Brain trading system. In this role, Claudius:

- Designs and refines trading agent prompts (optimized for Llama 3.3 70B)
- Writes Python code for data pipelines, backtesting, and execution
- Analyzes trade logs and backtest results
- Monitors system health across Vigil, Lumen, and Echelon nodes
- Produces deployment-ready artifacts pushed via git + SSH

But Claudius is general-purpose — it can be configured for any long-running AI assistant workflow.

## Quick Start

### Prerequisites
- Python 3.11+
- Claude Code CLI installed and authenticated (`claude --version`)
- Docker (for containerized deployment)
- Slack Bot + App Tokens (for messaging bridge)

### Local Development
```bash
git clone https://github.com/vonstegen/claudius.git
cd claudius
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp config/config.example.yaml config/config.yaml
# Edit config.yaml with your settings
python -m src.daemon
```

### Docker Deployment (Recommended for Lumen)
```bash
docker compose up -d
```

## Project Structure

```
claudius/
├── src/                    # Core daemon source code
│   ├── __init__.py
│   ├── daemon.py           # Main entry point, lifecycle management
│   ├── bridge/             # Messaging bridges (Telegram, Slack, etc.)
│   │   ├── __init__.py
│   │   ├── base.py         # Abstract bridge interface
│   │   └── telegram.py     # Telegram bot bridge
│   ├── scheduler.py        # Heartbeat / cron task scheduler
│   ├── session.py          # Claude Code session manager
│   ├── memory.py           # Persistent memory layer
│   ├── router.py           # Task routing and delegation
│   └── skills.py           # Skills loader and executor
├── skills/                 # Markdown skill playbooks
│   ├── README.md
│   ├── system-health.md    # Check Triune Brain node status
│   ├── code-review.md      # Review and analyze code changes
│   └── daily-report.md     # Generate daily summary
├── memory/                 # Persistent memory storage
│   ├── MEMORY.md           # Running context (auto-updated)
│   └── conversations/      # Conversation logs
├── prompts/                # System prompts and templates
│   ├── CLAUDIUS.md         # Core system prompt
│   └── agents/             # Sub-agent prompt definitions
├── config/                 # Configuration files
│   ├── config.example.yaml # Template config
│   └── config.yaml         # Active config (gitignored)
├── scripts/                # Utility scripts
│   ├── setup.sh            # First-time setup
│   ├── health-check.sh     # System health verification
│   └── deploy-to-lumen.sh  # Deploy to production machine
├── tests/                  # Test suite
│   ├── __init__.py
│   ├── test_daemon.py
│   ├── test_bridge.py
│   └── test_memory.py
├── docs/                   # Documentation
│   ├── ARCHITECTURE.md     # System design
│   ├── DEPLOYMENT.md       # Deployment guide
│   └── SKILLS-GUIDE.md     # How to write skills
├── docker-compose.yaml     # Docker deployment
├── Dockerfile              # Container image
├── requirements.txt        # Python dependencies
├── pyproject.toml          # Project metadata
├── .env.example            # Environment variable template
├── .gitignore
├── LICENSE
└── README.md               # This file
```

## Configuration

Copy `config/config.example.yaml` to `config/config.yaml` and edit:

```yaml
# Core settings
claude_code:
  workspace: ~/claudius
  model: opus  # or sonnet
  headless: true

# Messaging bridges
bridges:
  telegram:
    enabled: true
    bot_token: ${TELEGRAM_BOT_TOKEN}
    allowed_users:
      - your_telegram_user_id

# Heartbeat scheduler
scheduler:
  enabled: true
  jobs:
    - name: health-check
      skill: system-health
      cron: "*/30 * * * *"  # Every 30 minutes
    - name: daily-report
      skill: daily-report
      cron: "0 8 * * *"     # 8 AM daily

# Memory
memory:
  backend: sqlite  # or file
  db_path: memory/claudius.db
  max_context_tokens: 50000

# Triune Brain integration
triune_brain:
  vigil:
    host: gx10-b71c
    ollama_port: 11434
  lumen:
    host: desktop-rssp6ga-1
  echelon:
    host: avs-dellxps
  repo: ~/forex-agent
```

## Writing Skills

Skills are markdown files in `skills/` that Claudius loads and follows. See [Skills Guide](docs/SKILLS-GUIDE.md).

```markdown
# Skill: System Health Check

## Trigger
On schedule (every 30 min) or when operator asks "check health"

## Steps
1. SSH to each Triune Brain node and run health-check.sh
2. Check Ollama is responding on Vigil (:11434)
3. Check PostgreSQL and Redis on Lumen
4. Check disk space on all nodes
5. Report status via messaging bridge
6. If any node is unhealthy, alert operator immediately

## Output
Brief status message: all green, or specific issues found.
```

## Roadmap

- [x] Project structure and architecture
- [ ] Core daemon with lifecycle management
- [ ] Telegram messaging bridge
- [ ] Claude Code session manager (headless)
- [ ] Persistent memory layer (SQLite + markdown)
- [ ] Skills loader and executor
- [ ] Heartbeat scheduler (cron)
- [ ] Task router with sub-agent delegation
- [ ] Docker containerization
- [ ] Triune Brain integration skills
- [ ] Slack bridge
- [ ] Web dashboard (optional)
- [ ] Voice interface (optional)

## Related Projects

- [forex-agent](https://github.com/vonstegen/forex-agent) — The Triune Brain trading system that Claudius architects
- [Claude Code](https://docs.anthropic.com/claude-code) — The underlying AI engine
- [Jinn](https://github.com/search?q=jinn+claude+code) — Similar Claude Code wrapper (community)

## License

MIT

## Author

Andreas von Stegen — ajoechl@pm.me
