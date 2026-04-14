# Skill: Code Review

## Trigger
When operator asks "review code" / "check changes" / "what changed"

## Steps

1. **Get recent changes**
   - Run: `cd ~/forex-agent && git log --oneline -10`
   - Run: `cd ~/forex-agent && git diff HEAD~1 --stat`

2. **Review the diff**
   - Run: `cd ~/forex-agent && git diff HEAD~1`
   - Analyze for: bugs, security issues, missing error handling, style problems

3. **Check test status**
   - Run: `cd ~/forex-agent && python -m pytest tests/ -v --tb=short 2>&1 | tail -30`

## Output
Brief review:
- Summary of changes (what was modified and why)
- Any issues found (bugs, security, style)
- Test results (pass/fail count)
- Recommendation: ship it, needs fixes, or needs discussion
