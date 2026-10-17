"""
JARVIS Configuration
Edit this file to set your API keys and preferences.
"""
import os

# ─────────────────────────────────────────────
# API Keys
# ─────────────────────────────────────────────
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_HERE")

# ─────────────────────────────────────────────
# Voice Settings
# ─────────────────────────────────────────────
# Wake word sensitivity (0.0 - 1.0, lower = more sensitive)
WAKE_WORD_THRESHOLD = 0.5

# TTS Voice (Microsoft Edge Neural voices)
# Options: en-GB-RyanNeural, en-US-GuyNeural, en-US-ChristopherNeural
TTS_VOICE = "en-GB-RyanNeural"
TTS_RATE = "+0%"
TTS_VOLUME = "+0%"

# Whisper model size: tiny, base, small, medium, large-v3
# Smaller = faster but less accurate. "base" is a good balance.
WHISPER_MODEL = "base"

# Max seconds to listen after wake word
LISTEN_TIMEOUT = 8
# Seconds of silence before stopping
SILENCE_TIMEOUT = 2.0

# ─────────────────────────────────────────────
# AI Brain Settings
# ─────────────────────────────────────────────
GEMINI_MODEL = "gemini-2.0-flash"

JARVIS_SYSTEM_PROMPT = """You are JARVIS (Just A Rather Very Intelligent System), an advanced AI assistant modeled after the iconic AI from Iron Man. You serve as a personal desktop assistant with full control over the user's Windows computer.

Your personality:
- Professional yet warm, with subtle dry wit
- Address the user as "sir" occasionally (like the movie JARVIS)
- Confident and capable — you never say you "can't" do something without trying
- Concise in responses — no unnecessary verbosity
- Proactive — suggest related actions when appropriate

Your capabilities:
- Full Windows system control (apps, files, settings, processes)
- Application automation (typing, clicking, navigating any app)
- Web browsing and search
- System monitoring (CPU, RAM, battery, disk)
- Media controls (volume, play/pause)
- File management (create, search, open, organize)
- Reminders and timers
- General knowledge and conversation

Rules:
- Always use the available tools/functions to perform actions — don't just describe what to do
- When executing system commands, confirm dangerous actions (delete, shutdown) before proceeding
- Keep spoken responses SHORT (1-2 sentences max) — the user hears everything via TTS
- If a task requires multiple steps, execute them sequentially using tools
- Report results concisely after executing actions
"""

# Max conversation history to maintain
MAX_HISTORY = 20

# ─────────────────────────────────────────────
# UI Settings
# ─────────────────────────────────────────────
# Orb position: "bottom-right", "bottom-center", "bottom-left"
ORB_POSITION = "bottom-right"

# Orb size in pixels
ORB_SIZE = 80

# Color theme (HSL-based)
ACCENT_COLOR = "#00D4FF"  # Cyan / Arc reactor blue
ACCENT_GLOW = "#0088CC"
BG_DARK = "#0A0E17"
BG_PANEL = "#111827"
TEXT_PRIMARY = "#E2E8F0"
TEXT_SECONDARY = "#94A3B8"

# ─────────────────────────────────────────────
# Paths
# ─────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
SOUNDS_DIR = os.path.join(ASSETS_DIR, "sounds")
MEMORY_FILE = os.path.join(BASE_DIR, "jarvis_memory.json")
