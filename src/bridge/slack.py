"""
Slack Bridge — Routes messages between Slack and Claudius.

Uses Slack's Socket Mode (no public URL needed) to receive messages
from authorized channels/users, passes them to the task router,
and sends responses back.
"""

import logging
import os
import re

from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler

from src.bridge.base import BaseBridge

logger = logging.getLogger("claudius.bridge.slack")


class SlackBridge(BaseBridge):
    """Slack bot bridge for Claudius using Socket Mode."""

    def __init__(self, config: dict, router):
        self.bot_token = config["bot_token"]
        self.app_token = config["app_token"]
        self.allowed_channels = config.get("allowed_channels", [])
        self.allowed_users = [str(u) for u in config.get("allowed_users", [])]
        self.router = router
        self.app = AsyncApp(token=self.bot_token)
        self.handler = None
        self._register_handlers()

    def _is_authorized(self, user_id: str, channel_id: str) -> bool:
        """Check if user/channel is authorized."""
        if self.allowed_users and user_id not in self.allowed_users:
            return False
        if self.allowed_channels and channel_id not in self.allowed_channels:
            return False
        return True

    def _register_handlers(self):
        """Register Slack event handlers."""

        @self.app.event("app_mention")
        async def handle_mention(event, say):
            """Respond when @Claudius is mentioned."""
            await self._process_message(event, say)

        @self.app.event("message")
        async def handle_dm(event, say):
            """Respond to direct messages."""
            # Only handle DMs (channel type 'im'), skip bot messages
            if event.get("channel_type") != "im":
                return
            if event.get("bot_id"):
                return
            await self._process_message(event, say)

        @self.app.command("/claudius")
        async def handle_command(ack, command, say):
            """Handle /claudius slash command."""
            await ack()
            user_id = command.get("user_id", "")
            channel_id = command.get("channel_id", "")

            if not self._is_authorized(user_id, channel_id):
                await say("Unauthorized.")
                return

            user_msg = command.get("text", "").strip()
            if not user_msg:
                await say(
                    "🏛️ *Claudius is online.*\n\n"
                    "Usage: `/claudius <your message>`\n"
                    "Or mention me: `@Claudius check health`\n\n"
                    "Commands:\n"
                    "• `/claudius status` — System status\n"
                    "• `/claudius skills` — List available skills\n"
                    "• `/claudius health` — Triune Brain health check"
                )
                return

            logger.info(f"Slack command [{user_id}]: {user_msg[:80]}...")
            response = await self.router.handle(
                message=user_msg,
                source="slack",
                metadata={"user_id": user_id, "channel_id": channel_id},
            )
            await self._send_chunked(say, response)

    async def _process_message(self, event: dict, say):
        """Process an incoming Slack message."""
        user_id = event.get("user", "")
        channel_id = event.get("channel", "")
        text = event.get("text", "").strip()

        if not text or not self._is_authorized(user_id, channel_id):
            return

        # Strip bot mention from text if present
        text = re.sub(r"<@\w+>\s*", "", text).strip()
        if not text:
            return

        logger.info(f"Slack [{user_id}]: {text[:80]}...")

        response = await self.router.handle(
            message=text,
            source="slack",
            metadata={"user_id": user_id, "channel_id": channel_id},
        )
        await self._send_chunked(say, response)

    async def _send_chunked(self, say, text: str):
        """Send response, splitting if it exceeds Slack's 4000 char limit."""
        for i in range(0, len(text), 3900):
            chunk = text[i : i + 3900]
            await say(chunk)

    async def start(self):
        """Start the Slack bot in Socket Mode."""
        logger.info("Slack bridge starting (Socket Mode)")
        self.handler = AsyncSocketModeHandler(self.app, self.app_token)
        await self.handler.start_async()

    async def stop(self):
        """Stop the Slack bot."""
        if self.handler:
            await self.handler.close_async()
            logger.info("Slack bridge stopped")

    async def send_message(self, channel_id: str, text: str):
        """Send a proactive message to a channel."""
        await self.app.client.chat_postMessage(
            channel=channel_id,
            text=text[:3900],
        )
