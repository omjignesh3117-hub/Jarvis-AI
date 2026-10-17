"""
JARVIS App Controller
Advanced application automation using pywinauto and pyautogui.
"""
import logging
import time

import pyautogui

logger = logging.getLogger("jarvis.app")

# Safety: disable pyautogui fail-safe (mouse to corner = stop)
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1


class AppController:
    """Automate application interaction."""

    @staticmethod
    def send_keys(keys: str, interval: float = 0.05) -> str:
        """Type text or send key combinations.

        For hotkeys use '+' separator: 'ctrl+c', 'alt+f4', 'win+e'
        For regular text, just pass the string.
        """
        try:
            # Check if it's a hotkey combination
            hotkey_indicators = ["+"]
            key_names = [
                "ctrl", "alt", "shift", "win", "enter", "tab", "escape",
                "backspace", "delete", "space", "up", "down", "left", "right",
                "home", "end", "pageup", "pagedown", "f1", "f2", "f3", "f4",
                "f5", "f6", "f7", "f8", "f9", "f10", "f11", "f12",
            ]

            keys_lower = keys.lower().strip()
            parts = [k.strip() for k in keys_lower.split("+")]

            if len(parts) > 1 and any(p in key_names for p in parts):
                # It's a hotkey
                pyautogui.hotkey(*parts)
                return f"Pressed hotkey: {keys}"
            elif keys_lower in key_names:
                pyautogui.press(keys_lower)
                return f"Pressed key: {keys}"
            else:
                # Regular text
                pyautogui.typewrite(keys, interval=interval)
                return f"Typed: {keys}"
        except Exception as e:
            return f"Error sending keys: {e}"

    @staticmethod
    def click_at(x: int, y: int, button: str = "left", clicks: int = 1) -> str:
        """Click at specific screen coordinates."""
        try:
            pyautogui.click(x=x, y=y, button=button, clicks=clicks)
            return f"Clicked at ({x}, {y})."
        except Exception as e:
            return f"Error clicking: {e}"

    @staticmethod
    def move_mouse(x: int, y: int) -> str:
        """Move mouse to specific coordinates."""
        try:
            pyautogui.moveTo(x, y, duration=0.3)
            return f"Mouse moved to ({x}, {y})."
        except Exception as e:
            return f"Error moving mouse: {e}"

    @staticmethod
    def scroll(amount: int) -> str:
        """Scroll up (positive) or down (negative)."""
        try:
            pyautogui.scroll(amount)
            direction = "up" if amount > 0 else "down"
            return f"Scrolled {direction} by {abs(amount)}."
        except Exception as e:
            return f"Error scrolling: {e}"

    @staticmethod
    def get_mouse_position() -> str:
        """Get current mouse position."""
        pos = pyautogui.position()
        return f"Mouse is at ({pos.x}, {pos.y})."

    @staticmethod
    def get_screen_size() -> str:
        """Get screen resolution."""
        size = pyautogui.size()
        return f"Screen resolution: {size.width}x{size.height}"

    @staticmethod
    def focus_window(title: str) -> str:
        """Bring a window to the foreground by title."""
        try:
            from pywinauto import Desktop

            desktop = Desktop(backend="uia")
            windows = desktop.windows()

            for w in windows:
                if title.lower() in w.window_text().lower():
                    w.set_focus()
                    return f"Focused window: {w.window_text()}"

            return f"Window '{title}' not found."
        except Exception as e:
            return f"Error focusing window: {e}"

    @staticmethod
    def list_windows() -> str:
        """List all visible windows."""
        try:
            from pywinauto import Desktop

            desktop = Desktop(backend="uia")
            windows = desktop.windows()

            visible = []
            for w in windows:
                text = w.window_text()
                if text and text.strip():
                    visible.append(text)

            if visible:
                return "Open windows:\n" + "\n".join(f"  • {w}" for w in visible[:20])
            else:
                return "No visible windows found."
        except Exception as e:
            return f"Error listing windows: {e}"

    @staticmethod
    def type_text(text: str) -> str:
        """Type text naturally (supports unicode, unlike typewrite)."""
        try:
            import pyperclip
            # Use clipboard method for unicode support
            old_clip = ""
            try:
                old_clip = pyperclip.paste()
            except Exception:
                pass

            pyperclip.copy(text)
            pyautogui.hotkey("ctrl", "v")
            time.sleep(0.2)

            # Restore old clipboard
            try:
                pyperclip.copy(old_clip)
            except Exception:
                pass

            return f"Typed text ({len(text)} chars)."
        except ImportError:
            # Fallback without pyperclip
            pyautogui.typewrite(text, interval=0.02)
            return f"Typed text ({len(text)} chars)."
        except Exception as e:
            return f"Error typing: {e}"
