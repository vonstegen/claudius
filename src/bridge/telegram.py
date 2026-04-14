"""
Telegram Bridge — Routes messages between Telegram and Claudius.

Receives messages from authorized users, passes them to the task router,
and sends responses back.
"""

import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters

from src.bridge.base import BaseBridge

logger = logging.getLogger("claudius.bridge.telegram")


class TelegramBridge(BaseBridge):
    """Telegram bot bridge for Claudius."""

    def __init__(self, config: dict, router):
        self.token = config["bot_token"]
        self.allowed_users = [str(u) for u in config.get("allowed_users", [])]
        self.router = router
        self.app = None

    def _is_authorized(self, user_id: int) -> bool:
        """Check if user is in the allowed list."""
        if not self.allowed_users:
            return True  # No whitelist = allow all (not recommended)
        return str(user_id) in self.allowed_users

    async def _handle_message(self, update: Update, context):
        """Handle incoming Telegram messages."""
        if not update.message or not update.message.text:
            return
        if not self._is_authorized(update.effective_user.id):
            logger.warning(f"Unauthorized user: {update.effective_user.id}")
            return

        user_msg = update.message.text
        logger.info(f"Telegram [{update.effective_user.first_name}]: {user_msg[:80]}...")

        # Send typing indicator
        await update.message.chat.send_action("typing")

        # Route to Claudius
        response = await self.router.handle(
            message=user_msg,
            source="telegram",
            metadata={"user_id": str(update.effective_user.id)},
        )

        # Send response (split if too long for Telegram's 4096 char limit)
        for i in range(0, len(response), 4000):
            await update.message.reply_text(response[i : i + 4000])

    async def _handle_start(self, update: Update, context):
        """Handle /start command."""
        if not self._is_authorized(update.effective_user.id):
            return
        await update.message.reply_text(
            "🏛️ Claudius is online.\n\n"
            "Send me a message and I'll process it. Commands:\n"
            "/status — System status\n"
            "/skills — List available skills\n"
            "/health — Triune Brain health check"
        )

    async def _handle_status(self, update: Update, context):
        """Handle /status command."""
        if not self._is_authorized(update.effective_user.id):
            return
        response = await self.router.handle(
            message="Give me a brief status update on Claudius and the Triune Brain.",
            source="telegram",
            metadata={"user_id": str(update.effective_user.id)},
        )
        await update.message.reply_text(response[:4000])

    async def start(self):
        """Start the Telegram bot."""
        self.app = Application.builder().token(self.token).build()

        # Register handlers
        self.app.add_handler(CommandHandler("start", self._handle_start))
        self.app.add_handler(CommandHandler("status", self._handle_status))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_message))

        logger.info("Telegram bridge starting (polling mode)")
        await self.app.initialize()
        await self.app.start()
        await self.app.updater.start_polling(drop_pending_updates=True)

    async def stop(self):
        """Stop the Telegram bot."""
        if self.app:
            await self.app.updater.stop()
            await self.app.stop()
            await self.app.shutdown()
            logger.info("Telegram bridge stopped")

    async def send_message(self, chat_id: str, text: str):
        """Send a proactive message to a chat."""
        if self.app:
            await self.app.bot.send_message(chat_id=chat_id, text=text[:4000])
