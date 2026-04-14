"""Abstract base class for messaging bridges."""

from abc import ABC, abstractmethod


class BaseBridge(ABC):
    """Interface that all messaging bridges must implement."""

    @abstractmethod
    async def start(self):
        """Start listening for messages."""

    @abstractmethod
    async def stop(self):
        """Stop the bridge gracefully."""

    @abstractmethod
    async def send_message(self, chat_id: str, text: str):
        """Send a message to a specific chat."""
