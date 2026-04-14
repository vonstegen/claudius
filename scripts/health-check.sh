#!/usr/bin/env bash
# Quick health check for Claudius and Triune Brain
# Run: bash scripts/health-check.sh

echo "🏛️  Claudius Health Check"
echo "========================"

# Claudius daemon
if [ -f /tmp/claudius.pid ] && kill -0 "$(cat /tmp/claudius.pid)" 2>/dev/null; then
    echo "✅ Claudius daemon: running (PID $(cat /tmp/claudius.pid))"
else
    echo "❌ Claudius daemon: not running"
fi

# Vigil / Ollama
if curl -sf http://gx10-b71c:11434/ >/dev/null 2>&1; then
    MODELS=$(curl -sf http://gx10-b71c:11434/api/tags | python3 -c "import sys,json; [print(f'   - {m[\"name\"]}') for m in json.load(sys.stdin).get('models',[])]" 2>/dev/null)
    echo "✅ Vigil (Ollama): responding"
    echo "$MODELS"
else
    echo "❌ Vigil (Ollama): not responding"
fi

# PostgreSQL
if pg_isready -h localhost -p 5432 -q 2>/dev/null; then
    echo "✅ PostgreSQL: ready"
else
    echo "❌ PostgreSQL: not ready"
fi

# Redis
if redis-cli ping 2>/dev/null | grep -q PONG; then
    echo "✅ Redis: responding"
else
    echo "❌ Redis: not responding"
fi

# DuckDB
if [ -f ~/forex-agent/data/forex.duckdb ]; then
    SIZE=$(du -sh ~/forex-agent/data/forex.duckdb | cut -f1)
    echo "✅ DuckDB: present ($SIZE)"
else
    echo "⚠️  DuckDB: file not found"
fi

# Echelon
if ssh -o ConnectTimeout=2 -o BatchMode=yes avs-dellxps 'echo ok' 2>/dev/null; then
    echo "✅ Echelon: reachable"
else
    echo "⚠️  Echelon: offline (may be normal)"
fi
