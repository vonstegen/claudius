"""
Claudius Daemon — Main entry point and lifecycle manager.

Starts the messaging bridge, scheduler, and session manager.
Handles graceful shutdown and crash recovery.
"""

import asyncio
import logging
import os
import signal
import sys
from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console
from rich.logging import RichHandler

from src.config import load_config
from src.memory import MemoryStore
from src.session import ClaudeSession
from src.scheduler import Scheduler
from src.skills import SkillLoader
from src.router import TaskRouter

console = Console()
logger = logging.getLogger("claudius")


class ClaudiusDaemon:
    """Main daemon process that orchestrates all Claudius components."""

    def __init__(self, config_path: str = "config/config.yaml"):
        load_dotenv()
        self.config = load_config(config_path)
        self.running = False
        self.components = {}

        # Setup logging
        log_level = self.config.get("daemon", {}).get("log_level", "INFO")
        logging.basicConfig(
            level=getattr(logging, log_level),
            format="%(message)s",
            datefmt="%H:%M:%S",
            handlers=[RichHandler(console=console, rich_tracebacks=True)],
        )

    async def start(self):
        """Initialize and start all components."""
        logger.info("🏛️  Claudius starting up...")

        # Write PID file
        pid_file = self.config.get("daemon", {}).get("pid_file", "/tmp/claudius.pid")
        Path(pid_file).write_text(str(os.getpid()))

        # Initialize components
        self.components["memory"] = MemoryStore(self.config.get("memory", {}))
        await self.components["memory"].initialize()
        logger.info("  ✓ Memory store initialized")

        self.components["skills"] = SkillLoader(self.config.get("skills", {}))
        self.components["skills"].load_all()
        logger.info(f"  ✓ Loaded {len(self.components['skills'].skills)} skills")

        self.components["session"] = ClaudeSession(self.config.get("claude_code", {}))
        logger.info("  ✓ Claude Code session manager ready")

        self.components["router"] = TaskRouter(
            session=self.components["session"],
            memory=self.components["memory"],
            skills=self.components["skills"],
        )
        logger.info("  ✓ Task router ready")

        # Start scheduler
        if self.config.get("scheduler", {}).get("enabled", False):
            self.components["scheduler"] = Scheduler(
                config=self.config.get("scheduler", {}),
                router=self.components["router"],
            )
            self.components["scheduler"].start()
            logger.info("  ✓ Scheduler started")

        # Start messaging bridges
        bridges_config = self.config.get("bridges", {})
        if bridges_config.get("slack", {}).get("enabled", False):
            from src.bridge.slack import SlackBridge

            bridge = SlackBridge(
                config=bridges_config["telegram"],
                router=self.components["router"],
            )
            self.components["slack_bridge"] = bridge
            asyncio.create_task(bridge.start())
            logger.info("  ✓ Slack bridge started")

        self.running = True
        logger.info("🏛️  Claudius is operational")

        # Keep alive
        while self.running:
            await asyncio.sleep(1)

    async def shutdown(self):
        """Graceful shutdown of all components."""
        logger.info("🏛️  Claudius shutting down...")
        self.running = False

        # Stop bridges
        for name, component in self.components.items():
            if hasattr(component, "stop"):
                await component.stop() if asyncio.iscoroutinefunction(component.stop) else component.stop()
                logger.info(f"  ✓ {name} stopped")

        # Remove PID file
        pid_file = self.config.get("daemon", {}).get("pid_file", "/tmp/claudius.pid")
        Path(pid_file).unlink(missing_ok=True)

        logger.info("🏛️  Claudius stopped")


def main():
    """Entry point."""
    daemon = ClaudiusDaemon()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Signal handlers
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, lambda: asyncio.ensure_future(daemon.shutdown()))

    try:
        loop.run_until_complete(daemon.start())
    except KeyboardInterrupt:
        loop.run_until_complete(daemon.shutdown())
    finally:
        loop.close()


if __name__ == "__main__":
    main()
