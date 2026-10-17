"""
JARVIS Memory System
Manages conversation history and persistent memory.
"""
import json
import logging
import os
from datetime import datetime

logger = logging.getLogger("jarvis.memory")


class Memory:
    """Conversation history and persistent memory manager."""

    def __init__(self, config):
        self.config = config
        self.conversation = []
        self.max_history = config.MAX_HISTORY
        self.memory_file = config.MEMORY_FILE
        self._load_memory()

    def add_user_message(self, text):
        """Add a user message to conversation history."""
        self.conversation.append({
            "role": "user",
            "parts": [{"text": text}],
            "timestamp": datetime.now().isoformat()
        })
        self._trim_history()
        self._save_memory()

    def add_assistant_message(self, text):
        """Add an assistant message to conversation history."""
        self.conversation.append({
            "role": "model",
            "parts": [{"text": text}],
            "timestamp": datetime.now().isoformat()
        })
        self._trim_history()
        self._save_memory()

    def get_history_for_api(self):
        """Get conversation history formatted for Gemini API."""
        history = []
        for msg in self.conversation:
            history.append({
                "role": msg["role"],
                "parts": msg["parts"]
            })
        return history

    def clear(self):
        """Clear conversation history."""
        self.conversation = []
        self._save_memory()

    def _trim_history(self):
        """Keep only the last N messages."""
        if len(self.conversation) > self.max_history:
            self.conversation = self.conversation[-self.max_history:]

    def _save_memory(self):
        """Persist conversation to disk."""
        try:
            data = {
                "conversation": self.conversation,
                "last_updated": datetime.now().isoformat()
            }
            with open(self.memory_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save memory: {e}")

    def _load_memory(self):
        """Load persisted conversation from disk."""
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.conversation = data.get("conversation", [])
                logger.info(f"Loaded {len(self.conversation)} messages from memory.")
        except Exception as e:
            logger.error(f"Failed to load memory: {e}")
            self.conversation = []
