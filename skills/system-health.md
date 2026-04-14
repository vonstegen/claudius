# Skill: System Health Check

## Trigger
Scheduled every 30 minutes, or when operator asks "check health" / "system status"

## Steps

1. **Check Vigil (Ollama)**
   - Run: `curl -s http://gx10-b71c:11434/api/tags | head -5`
   - Verify Llama 3.3 70B is listed
   - Run: `ssh gx10-b71c 'uptime && free -h | head -2 && df -h / | tail -1'`

2. **Check Lumen (Local — databases)**
   - Run: `systemctl is-active postgresql redis-server`
   - Run: `pg_isready -h localhost -p 5432`
   - Run: `redis-cli ping`
   - Run: `du -sh ~/forex-agent/data/forex.duckdb`

3. **Check Echelon (SSH)**
   - Run: `ssh avs-dellxps 'uptime'`
   - Verify connectivity only — Echelon may be off if operator isn't working

4. **Check forex-agent repo**
   - Run: `cd ~/forex-agent && git status --short && git log --oneline -3`

## Output
Report status as a brief summary:
- ✅ Vigil: Ollama responding, 70B model loaded, [uptime]
- ✅ Lumen: PostgreSQL up, Redis up, DuckDB [size]
- ✅/⚠️ Echelon: Reachable / Offline (OK if outside work hours)
- 📊 Repo: [branch], [last 3 commits]

If anything is unhealthy, flag it prominently and suggest remediation.
