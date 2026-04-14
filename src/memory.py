"""
Persistent Memory Store.

Provides conversation history, context management, and state persistence
across daemon restarts. Uses SQLite for structured data and markdown for
human-readable context.
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger("claudius.memory")


class MemoryStore:
    """SQLite-backed persistent memory with markdown export."""

    def __init__(self, config: dict):
        self.db_path = Path(config.get("db_path", "memory/claudius.db"))
        self.md_path = Path(config.get("markdown_path", "memory/MEMORY.md"))
        self.conv_path = Path(config.get("conversation_path", "memory/conversations"))
        self.max_context = config.get("max_context_tokens", 50000)
        self.db = None

    async def initialize(self):
        """Create database and tables if they don't exist."""
        import aiosqlite

        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conv_path.mkdir(parents=True, exist_ok=True)

        self.db = await aiosqlite.connect(str(self.db_path))
        await self.db.executescript("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                source TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS state (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                description TEXT NOT NULL,
                result TEXT,
                completed_at TEXT
            );
        """)
        await self.db.commit()
        logger.info(f"Memory store initialized at {self.db_path}")

    async def log_conversation(self, source: str, role: str, content: str):
        """Log a conversation message."""
        now = datetime.utcnow().isoformat()
        await self.db.execute(
            "INSERT INTO conversations (timestamp, source, role, content) VALUES (?, ?, ?, ?)",
            (now, source, role, content),
        )
        await self.db.commit()

    async def get_recent_context(self, limit: int = 20) -> str:
        """Get recent conversation messages as context string."""
        async with self.db.execute(
            "SELECT timestamp, source, role, content FROM conversations ORDER BY id DESC LIMIT ?",
            (limit,),
        ) as cursor:
            rows = await cursor.fetchall()

        if not rows:
            return ""

        lines = []
        for ts, source, role, content in reversed(rows):
            lines.append(f"[{ts}] {source}/{role}: {content[:500]}")
        return "\n".join(lines)

    async def set_state(self, key: str, value: str):
        """Set a persistent state value."""
        now = datetime.utcnow().isoformat()
        await self.db.execute(
            "INSERT OR REPLACE INTO state (key, value, updated_at) VALUES (?, ?, ?)",
            (key, value, now),
        )
        await self.db.commit()

    async def get_state(self, key: str, default: str = "") -> str:
        """Get a persistent state value."""
        async with self.db.execute(
            "SELECT value FROM state WHERE key = ?", (key,)
        ) as cursor:
            row = await cursor.fetchone()
        return row[0] if row else default

    async def update_markdown(self):
        """Export current state to MEMORY.md for Claude Code to read."""
        context = await self.get_recent_context(limit=50)
        self.md_path.parent.mkdir(parents=True, exist_ok=True)
        self.md_path.write_text(
            f"# Claudius Memory\n"
            f"*Auto-updated: {datetime.utcnow().isoformat()}*\n\n"
            f"## Recent Conversations\n{context}\n"
        )

    async def stop(self):
        """Close database connection."""
        if self.db:
            await self.db.close()
