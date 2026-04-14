# Skills Guide

## What is a Skill?

A skill is a markdown file in the `skills/` directory that describes a workflow Claudius should follow. When triggered, the skill content is injected into Claude Code's context as a playbook.

## Creating a Skill

1. Create a new `.md` file in `skills/` (e.g., `skills/my-task.md`)
2. Use this template:

```markdown
# Skill: Descriptive Name

## Trigger
Describe when this skill should run.

## Steps
1. Specific action with exact command
2. Next action
3. Decision point — if X then Y, else Z

## Output
What to report back.
```

3. Reference it in `config/config.yaml` for scheduling, or trigger it by name in conversation.

## Best Practices

- **Be specific.** Include exact shell commands, file paths, and expected output.
- **Be sequential.** Number your steps. Claude follows them in order.
- **Include error handling.** Tell Claudius what to do if a step fails.
- **Define output format.** Especially for scheduled skills sent via Telegram.
- **Keep it focused.** One skill = one workflow. Compose complex tasks from multiple skills.

## Triggering Skills

### By schedule (config.yaml)
```yaml
scheduler:
  jobs:
    - name: my-job
      skill: my-task      # matches skills/my-task.md
      cron: "0 */6 * * *"  # every 6 hours
```

### By message
Send "run the my-task skill" or just mention "my-task" in your message.

### By another skill
A skill can reference other skills: "First run the system-health skill, then..."
