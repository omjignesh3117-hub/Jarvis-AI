"""
J.A.R.V.I.S. — Just A Rather Very Intelligent System
Main entry point.

Usage:
    python main.py              # Normal launch
    python main.py --no-voice   # Launch without voice (text-only mode)
    python main.py --setup-key  # Set up Gemini API key
"""
import asyncio
import logging
import os
import sys
import threading
import argparse

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config

# ── Logging Setup ──
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(
            os.path.join(config.BASE_DIR, "jarvis.log"),
            encoding="utf-8"
        ),
    ]
)
logger = logging.getLogger("jarvis")


class Jarvis:
    """Main JARVIS orchestrator — ties together voice, brain, and UI."""

    def __init__(self, voice_enabled=True):
        self.voice_enabled = voice_enabled
        self.voice_engine = None
        self.brain = None
        self.overlay = None
        self.memory = None

    def start(self):
        """Launch JARVIS."""
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import Qt

        logger.info("=" * 50)
        logger.info(" J.A.R.V.I.S. Initializing...")
        logger.info("=" * 50)

        # ── Check API Key ──
        if config.GEMINI_API_KEY == "YOUR_GEMINI_API_KEY_HERE":
            print("\n" + "=" * 50)
            print(" JARVIS Setup Required")
            print("=" * 50)
            print("\n You need a Google Gemini API key to run JARVIS.")
            print(" Get one for free at: https://aistudio.google.com/apikey")
            print()
            key = input(" Paste your API key here: ").strip()
            if key:
                config.GEMINI_API_KEY = key
                # Save to config file
                self._save_api_key(key)
                print(" ✓ API key saved!")
            else:
                print(" ✗ No key provided. JARVIS will run in limited mode.")

        # ── Initialize Qt App ──
        app = QApplication(sys.argv)
        app.setApplicationName("JARVIS")
        app.setQuitOnLastWindowClosed(False)  # Keep running in tray

        # ── Initialize Memory ──
        from core.memory import Memory
        self.memory = Memory(config)
        logger.info("Memory initialized.")

        # ── Initialize Brain ──
        from core.brain import Brain
        self.brain = Brain(
            config,
            on_response=self._on_brain_response,
            on_action=self._on_brain_action
        )
        brain_ok = self.brain.initialize()
        if brain_ok:
            logger.info("Brain online.")
        else:
            logger.warning("Brain failed to initialize — check API key.")

        # ── Initialize UI ──
        from ui.overlay import JarvisOverlay
        self.overlay = JarvisOverlay(config)
        self.overlay.user_command.connect(self._on_user_command)
        self.overlay.show()
        logger.info("UI overlay active.")

        # ── Initialize Voice ──
        if self.voice_enabled:
            from core.voice_engine import VoiceEngine
            self.voice_engine = VoiceEngine(
                config,
                on_wake=self._on_wake,
                on_command=self._on_voice_command,
                on_state_change=self._on_state_change
            )
            self.voice_engine.start()
            logger.info("Voice engine active.")
        else:
            logger.info("Voice disabled — text-only mode.")

        # ── Greeting ──
        greeting = "JARVIS online. All systems operational, sir."
        self.overlay.show_response(greeting)

        if self.voice_enabled and self.voice_engine:
            threading.Thread(
                target=self.voice_engine.speak_sync,
                args=(greeting,),
                daemon=True
            ).start()

        logger.info("JARVIS is ready.")
        logger.info("Say 'Hello Jarvis' or click the orb to begin.")

        # ── Run ──
        sys.exit(app.exec())

    # ── Callbacks ──

    def _on_wake(self):
        """Called when wake word is detected."""
        logger.info("Wake word detected!")
        self.overlay.set_state("listening")

    def _on_voice_command(self, text: str):
        """Called when voice command is transcribed."""
        logger.info(f"Voice command: {text}")
        self._process_command(text)

    def _on_user_command(self, text: str):
        """Called when user sends a command via UI."""
        if text == "__MIC_TRIGGER__":
            # Force voice listen
            if self.voice_engine:
                self.voice_engine.force_listen()
                self.overlay.set_state("listening")
            return

        self._process_command(text)

    def _on_brain_response(self, text: str):
        """Called when brain produces a response."""
        self.overlay.show_response(text)
        self.overlay.set_state("speaking")

        if self.voice_engine:
            def speak_then_idle():
                self.voice_engine.speak_sync(text)
                self.overlay.set_state("idle")

            threading.Thread(target=speak_then_idle, daemon=True).start()
        else:
            self.overlay.set_state("idle")

    def _on_brain_action(self, action: str):
        """Called when brain is executing a tool."""
        self.overlay.show_action(action)

    def _on_state_change(self, state: str):
        """Called when voice engine state changes."""
        self.overlay.set_state(state)

    def _process_command(self, text: str):
        """Process a user command (from voice or text)."""
        # Show user message in chat
        self.overlay.add_user_message(text)
        self.overlay.set_state("processing")

        # Save to memory
        self.memory.add_user_message(text)

        # Process with brain (async)
        def on_result(result):
            self.memory.add_assistant_message(result)
            self._on_brain_response(result)

        self.brain.process_command_async(text, callback=on_result)

    def _save_api_key(self, key: str):
        """Save API key to config file."""
        try:
            config_path = os.path.join(config.BASE_DIR, "config.py")
            with open(config_path, "r", encoding="utf-8") as f:
                content = f.read()

            content = content.replace(
                'GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_HERE")',
                f'GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "{key}")'
            )

            with open(config_path, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            logger.error(f"Failed to save API key: {e}")


def main():
    parser = argparse.ArgumentParser(description="JARVIS AI Desktop Assistant")
    parser.add_argument(
        "--no-voice", action="store_true",
        help="Disable voice features (text-only mode)"
    )
    parser.add_argument(
        "--setup-key", action="store_true",
        help="Set up Gemini API key"
    )
    args = parser.parse_args()

    if args.setup_key:
        print("\n Get your free API key at: https://aistudio.google.com/apikey\n")
        key = input(" Paste your Gemini API key: ").strip()
        if key:
            jarvis = Jarvis()
            jarvis._save_api_key(key)
            print(" ✓ API key saved to config.py!")
        return

    jarvis = Jarvis(voice_enabled=not args.no_voice)
    jarvis.start()


if __name__ == "__main__":
    main()
