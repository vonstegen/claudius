# Skill: Daily Report

## Trigger
Scheduled at 8 AM EST weekdays, or when operator asks "daily report"

## Steps

1. **System health summary**
   - Run the system-health skill internally (don't duplicate output)

2. **Development progress**
   - Run: `cd ~/forex-agent && git log --since="yesterday" --oneline`
   - Summarize what was built/changed in the last 24 hours

3. **Data pipeline status**
   - Run: `cd ~/forex-agent && python -c "import duckdb; db=duckdb.connect('data/forex.duckdb'); print(db.sql('SELECT pair, timeframe, count(*), min(timestamp), max(timestamp) FROM fx_ohlcv GROUP BY pair, timeframe').fetchall())"`
   - Report row counts, date ranges, any gaps

4. **Phase progress**
   - Reference PHASE-STATUS.md in the Claudius project knowledge
   - Note what was completed, what's next

5. **Priorities for today**
   - Based on current phase and recent work, suggest 2-3 tasks for the day

## Output
A concise morning briefing formatted for Telegram:

🏛️ **Claudius Daily Report — [Date]**

**System:** [all green / issues]
**Yesterday:** [what was done]
**Data:** [pipeline status]
**Phase [N]:** [progress]
**Today's priorities:**
1. [task]
2. [task]
3. [task]
