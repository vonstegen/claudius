# Claudius Architecture

## System Overview

Claudius is a Python daemon that wraps the Claude Code CLI in persistent, always-on operation with messaging bridges, scheduled tasks, and file-based memory. It runs on the Lumen machine (the always-on desktop in the Triune Brain network).

## Component Diagram

```
Operator (phone/laptop)
    │
    │ Telegram / Slack
    ▼
┌─────────────────────────────────────────────┐
│ Claudius Daemon (Python, on Lumen)          │
│                                             │
│  ┌──────────────┐  ┌───────────────────┐    │
│  │ Telegram     │  │ Scheduler         │    │
│  │ Bridge       │  │ (APScheduler)     │    │
│  └──────┬───────┘  └──────┬────────────┘    │
│         │                 │                 │
│         ▼                 ▼                 │
│  ┌─────────────────────────────────────┐    │
│  │ Task Router                         │    │
│  │ - Skill matching                    │    │
│  │ - Memory context injection          │    │
│  │ - Response logging                  │    │
│  └──────────────┬──────────────────────┘    │
│                 │                           │
│                 ▼                           │
│  ┌─────────────────────────────────────┐    │
│  │ Claude Code CLI (headless)          │    │
│  │ - Reads CLAUDIUS.md prompt          │    │
│  │ - Executes tools (bash, files, SSH) │    │
│  │ - Returns structured responses      │    │
│  └─────────────────────────────────────┘    │
│                                             │
│  ┌──────────────┐  ┌───────────────────┐    │
│  │ Memory Store │  │ Skills Loader     │    │
│  │ (SQLite +    │  │ (Markdown files)  │    │
│  │  Markdown)   │  │                   │    │
│  └──────────────┘  └───────────────────┘    │
└─────────────────────────────────────────────┘
    │               │               │
    │ SSH           │ local         │ SSH
    ▼               ▼               ▼
  Vigil           Lumen           Echelon
  (Ollama)        (DBs, data)     (Git, dev)
```

## Key Design Decisions

### Why Claude Code CLI (not API)?
- Uses Max subscription credits (flat rate) instead of per-token API billing
- Claude Code has native tool use (bash, file editing, SSH) built in
- Headless mode (`claude -p --yes`) enables non-interactive operation
- Future Claude Code features (Agent Teams, Dispatch) are inherited automatically

### Why a Python daemon (not a Claude Code extension)?
- Full control over lifecycle, crash recovery, and scheduling
- Messaging bridges need their own event loops (Telegram bot polling)
- Memory persistence across Claude Code session restarts
- Can be containerized and deployed independently

### Why file-based skills (not hardcoded)?
- Skills can be added/edited without code changes
- Claude Code reads markdown natively — no parsing needed
- The operator (or Claudius itself) can create new skills
- Version-controlled alongside the project

### Why SQLite for memory (not PostgreSQL)?
- Claudius's memory is separate from the trading system's data
- SQLite is zero-config, file-based, and portable
- No dependency on Lumen's PostgreSQL (which serves forex-agent)
- Easy to backup, inspect, and reset

## Data Flow

### Incoming message (Telegram)
1. Telegram bridge receives message
2. Authorization check (user whitelist)
3. Router receives message
4. Router checks for skill match
5. Router gathers memory context (recent conversations)
6. Router sends message + context to Claude Code session
7. Claude Code processes, may execute tools (bash, SSH, file ops)
8. Response returned to router
9. Router logs exchange to memory
10. Router sends response back through bridge

### Scheduled task (cron)
1. APScheduler fires at configured time
2. Scheduler calls router with skill name
3. Router loads skill markdown
4. Router sends skill as context to Claude Code
5. Claude Code executes skill steps
6. Response logged to memory
7. If alerting needed, response sent via bridge

## Deployment

Claudius runs on Lumen because:
- Lumen is always on (desktop, not laptop)
- Direct access to trading databases (DuckDB, PostgreSQL, Redis)
- SSH connectivity to Vigil and Echelon via Tailscale
- Claude Code CLI authenticated and ready

Docker deployment is recommended for isolation and auto-restart.
See DEPLOYMENT.md for details.
