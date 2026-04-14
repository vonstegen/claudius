# Skills

Skills are markdown playbooks that Claudius follows when triggered. Each `.md` file in this directory is a skill.

## How Skills Work

1. Skills are loaded automatically when Claudius starts
2. They can be triggered by:
   - **Scheduler** — Cron jobs reference skills by filename (without `.md`)
   - **Message matching** — If a user message contains the skill name, it's injected as context
   - **Direct request** — "Run the system-health skill"
3. Claude Code reads the skill markdown and follows the steps

## Writing a Skill

Create a new `.md` file in this directory. Structure it like this:

```markdown
# Skill: Name Here

## Trigger
When this skill should run (schedule, keyword, etc.)

## Context
What Claudius needs to know before executing.

## Steps
1. First step
2. Second step
3. Third step

## Output
What to report back after completion.
```

## Available Skills

- `system-health.md` — Check Triune Brain node health
- `code-review.md` — Review recent git changes
- `daily-report.md` — Generate daily summary
