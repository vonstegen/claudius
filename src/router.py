"""
Task Router — Routes incoming messages to Claude Code with appropriate context.

Decides whether a message needs a skill, memory context, or direct handling.
Logs all interactions to the memory store.
"""

import logging

from src.session import ClaudeSession
from src.memory import MemoryStore
from src.skills import SkillLoader

logger = logging.getLogger("claudius.router")


class TaskRouter:
    """Routes tasks to Claude Code with skill/memory context."""

    def __init__(self, session: ClaudeSession, memory: MemoryStore, skills: SkillLoader):
        self.session = session
        self.memory = memory
        self.skills = skills

    async def handle(self, message: str, source: str = "direct", metadata: dict = None) -> str:
        """
        Process an incoming message.

        1. Check if it matches a skill trigger
        2. Gather memory context
        3. Send to Claude Code
        4. Log the exchange
        5. Return the response
        """
        metadata = metadata or {}

        # Log incoming message
        await self.memory.log_conversation(source, "user", message)

        # Check for skill references
        skill_content = self._match_skill(message, metadata)

        # Build context from memory
        recent_context = await self.memory.get_recent_context(limit=10)
        context_parts = []
        if recent_context:
            context_parts.append(f"## Recent conversation context\n{recent_context}")
        if skill_content:
            context_parts.append(f"## Skill playbook to follow\n{skill_content}")

        context = "\n\n".join(context_parts)

        # Send to Claude Code
        try:
            response = await self.session.send(message, context=context)
        except Exception as e:
            logger.error(f"Router error: {e}")
            response = f"Error processing request: {e}"

        # Log response
        await self.memory.log_conversation(source, "assistant", response)

        # Update markdown memory
        await self.memory.update_markdown()

        return response

    def _match_skill(self, message: str, metadata: dict) -> str | None:
        """Check if the message or metadata references a skill."""
        # Explicit skill from scheduler
        if "skill" in metadata:
            return self.skills.get(metadata["skill"])

        # Check for skill name mentions in message
        msg_lower = message.lower()
        for skill_name in self.skills.list_skills():
            if skill_name.replace("-", " ") in msg_lower:
                logger.info(f"Matched skill: {skill_name}")
                return self.skills.get(skill_name)

        return None
