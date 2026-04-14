"""
Claude Code Session Manager.

Wraps the Claude Code CLI to run in headless/project mode.
Sends tasks, receives responses, manages session lifecycle.
"""

import asyncio
import json
import logging
from pathlib import Path

logger = logging.getLogger("claudius.session")


class ClaudeSession:
    """Manages interaction with Claude Code CLI."""

    def __init__(self, config: dict):
        self.workspace = Path(config.get("workspace", "~/claudius")).expanduser()
        self.model = config.get("model", "opus")
        self.headless = config.get("headless", True)
        self.max_retries = config.get("max_retries", 3)
        self.timeout = config.get("session_timeout", 3600)

    async def send(self, message: str, context: str = "") -> str:
        """
        Send a message to Claude Code and return the response.

        Args:
            message: The user message / task
            context: Optional additional context to prepend

        Returns:
            Claude's response text
        """
        full_prompt = f"{context}\n\n{message}" if context else message

        # Build the claude command
        cmd = [
            "claude",
            "-p", str(self.workspace),
            "--model", self.model,
            "--output-format", "text",
        ]
        if self.headless:
            cmd.append("--yes")  # Auto-accept tool use

        logger.debug(f"Sending to Claude Code: {message[:100]}...")

        for attempt in range(self.max_retries):
            try:
                proc = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdin=asyncio.subprocess.PIPE,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                stdout, stderr = await asyncio.wait_for(
                    proc.communicate(input=full_prompt.encode()),
                    timeout=self.timeout,
                )

                if proc.returncode == 0:
                    response = stdout.decode().strip()
                    logger.debug(f"Response received ({len(response)} chars)")
                    return response
                else:
                    error = stderr.decode().strip()
                    logger.warning(f"Claude Code error (attempt {attempt + 1}): {error}")

            except asyncio.TimeoutError:
                logger.warning(f"Claude Code timeout (attempt {attempt + 1})")
            except Exception as e:
                logger.error(f"Session error (attempt {attempt + 1}): {e}")

        return "Error: Failed to get response from Claude Code after retries."

    async def send_with_skill(self, skill_content: str, user_input: str = "") -> str:
        """Send a skill playbook to Claude with optional user input."""
        context = f"Follow this skill playbook:\n\n{skill_content}"
        return await self.send(user_input or "Execute this skill now.", context=context)
