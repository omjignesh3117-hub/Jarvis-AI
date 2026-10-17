"""
JARVIS System Controller
Full Windows system control: apps, files, settings, processes.
"""
import ctypes
import logging
import os
import subprocess
import shutil
import platform
import json
from datetime import datetime

logger = logging.getLogger("jarvis.system")


class SystemController:
    """Controls Windows system functions."""

    # ── App Management ─────────────────────────────────

    @staticmethod
    def open_application(app_name: str) -> str:
        """Open an application by name. Supports common app names and full paths."""
        app_map = {
            "notepad": "notepad.exe",
            "calculator": "calc.exe",
            "paint": "mspaint.exe",
            "file explorer": "explorer.exe",
            "explorer": "explorer.exe",
            "cmd": "cmd.exe",
            "command prompt": "cmd.exe",
            "powershell": "powershell.exe",
            "terminal": "wt.exe",
            "windows terminal": "wt.exe",
            "task manager": "taskmgr.exe",
            "control panel": "control.exe",
            "settings": "ms-settings:",
            "snipping tool": "snippingtool.exe",
            "snip": "snippingtool.exe",
            "chrome": "chrome.exe",
            "google chrome": "chrome.exe",
            "firefox": "firefox.exe",
            "edge": "msedge.exe",
            "microsoft edge": "msedge.exe",
            "brave": "brave.exe",
            "vscode": "code",
            "visual studio code": "code",
            "vs code": "code",
            "word": "winword.exe",
            "excel": "excel.exe",
            "powerpoint": "powerpnt.exe",
            "outlook": "outlook.exe",
            "spotify": "spotify.exe",
            "discord": "discord.exe",
            "slack": "slack.exe",
            "zoom": "zoom.exe",
            "teams": "teams.exe",
            "microsoft teams": "teams.exe",
            "whatsapp": "whatsapp.exe",
            "telegram": "telegram.exe",
            "vlc": "vlc.exe",
            "obs": "obs64.exe",
            "obs studio": "obs64.exe",
            "steam": "steam.exe",
            "epic games": "EpicGamesLauncher.exe",
        }

        name_lower = app_name.lower().strip()
        executable = app_map.get(name_lower, app_name)

        try:
            if executable.startswith("ms-"):
                os.startfile(executable)
            else:
                subprocess.Popen(
                    executable,
                    shell=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                    if not executable.endswith(".exe")
                    else 0,
                )
            return f"Opened {app_name} successfully."
        except FileNotFoundError:
            # Try searching in common paths
            try:
                result = subprocess.run(
                    ["where", executable],
                    capture_output=True, text=True, timeout=5,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                if result.returncode == 0:
                    path = result.stdout.strip().split("\n")[0]
                    subprocess.Popen(path)
                    return f"Opened {app_name} successfully."
            except Exception:
                pass

            # Try Start Menu search
            try:
                subprocess.Popen(
                    f'powershell -c "Start-Process \'{app_name}\'"',
                    shell=True
                )
                return f"Attempting to open {app_name}."
            except Exception:
                pass

            return f"Could not find application: {app_name}"
        except Exception as e:
            return f"Error opening {app_name}: {e}"

    @staticmethod
    def close_application(app_name: str) -> str:
        """Close a running application by name."""
        try:
            import psutil
            name_lower = app_name.lower().strip()
            killed = False
            for proc in psutil.process_iter(["name", "pid"]):
                pname = proc.info["name"].lower() if proc.info["name"] else ""
                if name_lower in pname or f"{name_lower}.exe" == pname:
                    proc.terminate()
                    killed = True

            if killed:
                return f"Closed {app_name}."
            else:
                return f"No running process found for {app_name}."
        except Exception as e:
            return f"Error closing {app_name}: {e}"

    # ── File Operations ─────────────────────────────────

    @staticmethod
    def search_files(query: str, directory: str = None, max_results: int = 10) -> str:
        """Search for files by name pattern."""
        if directory is None:
            directory = os.path.expanduser("~")

        try:
            results = []
            for root, dirs, files in os.walk(directory):
                # Skip system/hidden dirs
                dirs[:] = [d for d in dirs if not d.startswith(".") and d not in
                           ["node_modules", "__pycache__", ".git", "AppData"]]
                for f in files:
                    if query.lower() in f.lower():
                        full_path = os.path.join(root, f)
                        results.append(full_path)
                        if len(results) >= max_results:
                            break
                if len(results) >= max_results:
                    break

            if results:
                return f"Found {len(results)} files:\n" + "\n".join(results)
            else:
                return f"No files matching '{query}' found in {directory}"
        except Exception as e:
            return f"Search error: {e}"

    @staticmethod
    def open_file(file_path: str) -> str:
        """Open a file with its default application."""
        try:
            if os.path.exists(file_path):
                os.startfile(file_path)
                return f"Opened {os.path.basename(file_path)}."
            else:
                return f"File not found: {file_path}"
        except Exception as e:
            return f"Error opening file: {e}"

    @staticmethod
    def create_file(file_path: str, content: str = "") -> str:
        """Create a new file with optional content."""
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return f"Created file: {file_path}"
        except Exception as e:
            return f"Error creating file: {e}"

    @staticmethod
    def delete_file(file_path: str) -> str:
        """Delete a file or folder (sends to recycle bin concept — actually deletes)."""
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
                return f"Deleted file: {file_path}"
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
                return f"Deleted folder: {file_path}"
            else:
                return f"Path not found: {file_path}"
        except Exception as e:
            return f"Error deleting: {e}"

    # ── System Settings ─────────────────────────────────

    @staticmethod
    def set_volume(level: int) -> str:
        """Set system volume (0-100)."""
        try:
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            from comtypes import CLSCTX_ALL
            from ctypes import cast, POINTER

            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(
                IAudioEndpointVolume._iid_, CLSCTX_ALL, None
            )
            volume = cast(interface, POINTER(IAudioEndpointVolume))

            # pycaw uses scalar 0.0 - 1.0
            scalar = max(0, min(100, level)) / 100.0
            volume.SetMasterVolumeLevelScalar(scalar, None)
            return f"Volume set to {level}%."
        except Exception as e:
            # Fallback using nircmd or PowerShell
            try:
                subprocess.run(
                    ["powershell", "-c",
                     f'(New-Object -ComObject WScript.Shell).SendKeys([char]173)'],
                    capture_output=True, timeout=5,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                return f"Attempted to set volume to {level}%."
            except Exception:
                return f"Error setting volume: {e}"

    @staticmethod
    def set_brightness(level: int) -> str:
        """Set screen brightness (0-100)."""
        try:
            import screen_brightness_control as sbc
            sbc.set_brightness(level)
            return f"Brightness set to {level}%."
        except Exception as e:
            return f"Error setting brightness: {e}"

    @staticmethod
    def lock_screen() -> str:
        """Lock the workstation."""
        try:
            ctypes.windll.user32.LockWorkStation()
            return "Screen locked."
        except Exception as e:
            return f"Error locking screen: {e}"

    @staticmethod
    def shutdown_pc(action: str = "shutdown") -> str:
        """Shutdown, restart, or sleep the PC."""
        try:
            if action == "shutdown":
                os.system("shutdown /s /t 5")
                return "Shutting down in 5 seconds."
            elif action == "restart":
                os.system("shutdown /r /t 5")
                return "Restarting in 5 seconds."
            elif action == "sleep":
                os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
                return "Going to sleep."
            elif action == "cancel":
                os.system("shutdown /a")
                return "Shutdown cancelled."
            else:
                return f"Unknown action: {action}. Use shutdown, restart, sleep, or cancel."
        except Exception as e:
            return f"Error: {e}"

    @staticmethod
    def toggle_wifi(enable: bool = True) -> str:
        """Enable or disable WiFi."""
        try:
            action = "enable" if enable else "disable"
            subprocess.run(
                ["netsh", "interface", "set", "interface", "Wi-Fi", action],
                capture_output=True, timeout=10,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            return f"WiFi {'enabled' if enable else 'disabled'}."
        except Exception as e:
            return f"Error toggling WiFi: {e}"

    # ── Process Management ──────────────────────────────

    @staticmethod
    def get_system_info() -> str:
        """Get current system resource usage."""
        try:
            import psutil

            cpu = psutil.cpu_percent(interval=1)
            ram = psutil.virtual_memory()
            disk = psutil.disk_usage("C:\\")
            battery = psutil.sensors_battery()

            info = {
                "cpu_percent": cpu,
                "ram_total_gb": round(ram.total / (1024 ** 3), 1),
                "ram_used_gb": round(ram.used / (1024 ** 3), 1),
                "ram_percent": ram.percent,
                "disk_total_gb": round(disk.total / (1024 ** 3), 1),
                "disk_used_gb": round(disk.used / (1024 ** 3), 1),
                "disk_percent": round(disk.percent, 1),
            }

            if battery:
                info["battery_percent"] = battery.percent
                info["battery_plugged"] = battery.power_plugged

            return json.dumps(info, indent=2)
        except Exception as e:
            return f"Error getting system info: {e}"

    @staticmethod
    def list_running_processes(top_n: int = 15) -> str:
        """List top running processes by memory usage."""
        try:
            import psutil
            procs = []
            for p in psutil.process_iter(["name", "pid", "memory_percent", "cpu_percent"]):
                try:
                    procs.append(p.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            procs.sort(key=lambda x: x.get("memory_percent", 0), reverse=True)
            top = procs[:top_n]

            lines = ["Top processes by memory:"]
            for p in top:
                lines.append(
                    f"  {p['name']} (PID {p['pid']}) — "
                    f"RAM: {p.get('memory_percent', 0):.1f}%, "
                    f"CPU: {p.get('cpu_percent', 0):.1f}%"
                )
            return "\n".join(lines)
        except Exception as e:
            return f"Error listing processes: {e}"

    @staticmethod
    def kill_process(process_name: str) -> str:
        """Kill a process by name."""
        try:
            result = subprocess.run(
                ["taskkill", "/f", "/im", f"{process_name}"],
                capture_output=True, text=True, timeout=10,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            if result.returncode == 0:
                return f"Killed process: {process_name}"
            else:
                return f"Could not kill {process_name}: {result.stderr.strip()}"
        except Exception as e:
            return f"Error killing process: {e}"

    # ── Clipboard ───────────────────────────────────────

    @staticmethod
    def read_clipboard() -> str:
        """Read current clipboard content."""
        try:
            import win32clipboard
            win32clipboard.OpenClipboard()
            try:
                data = win32clipboard.GetClipboardData()
                return f"Clipboard content: {data}"
            except TypeError:
                return "Clipboard is empty or contains non-text data."
            finally:
                win32clipboard.CloseClipboard()
        except Exception as e:
            return f"Error reading clipboard: {e}"

    @staticmethod
    def write_clipboard(text: str) -> str:
        """Write text to clipboard."""
        try:
            import win32clipboard
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(text)
            win32clipboard.CloseClipboard()
            return "Text copied to clipboard."
        except Exception as e:
            return f"Error writing to clipboard: {e}"

    # ── Screenshots ─────────────────────────────────────

    @staticmethod
    def take_screenshot(save_path: str = None) -> str:
        """Take a screenshot and save it."""
        try:
            import pyautogui
            if save_path is None:
                desktop = os.path.join(os.path.expanduser("~"), "Desktop")
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                save_path = os.path.join(desktop, f"screenshot_{timestamp}.png")

            screenshot = pyautogui.screenshot()
            screenshot.save(save_path)
            return f"Screenshot saved to: {save_path}"
        except Exception as e:
            return f"Error taking screenshot: {e}"

    # ── Web ─────────────────────────────────────────────

    @staticmethod
    def open_website(url: str) -> str:
        """Open a URL in the default browser."""
        try:
            import webbrowser
            if not url.startswith(("http://", "https://")):
                url = "https://" + url
            webbrowser.open(url)
            return f"Opened {url} in browser."
        except Exception as e:
            return f"Error opening URL: {e}"

    @staticmethod
    def web_search(query: str) -> str:
        """Search Google in the default browser."""
        try:
            import webbrowser
            import urllib.parse
            url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
            webbrowser.open(url)
            return f"Searching Google for: {query}"
        except Exception as e:
            return f"Error searching: {e}"

    # ── Utility ─────────────────────────────────────────

    @staticmethod
    def get_current_time() -> str:
        """Get current date and time."""
        now = datetime.now()
        return now.strftime("It's %I:%M %p on %A, %B %d, %Y")

    @staticmethod
    def run_shell_command(command: str) -> str:
        """Execute a shell command and return output."""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            output = result.stdout.strip() or result.stderr.strip()
            return output[:2000] if output else "Command executed successfully (no output)."
        except subprocess.TimeoutExpired:
            return "Command timed out after 30 seconds."
        except Exception as e:
            return f"Error running command: {e}"

    # ── Media Controls ──────────────────────────────────

    @staticmethod
    def control_media(action: str) -> str:
        """Control media playback (play/pause, next, previous, stop)."""
        try:
            import pyautogui

            actions = {
                "play": "playpause",
                "pause": "playpause",
                "play/pause": "playpause",
                "playpause": "playpause",
                "next": "nexttrack",
                "previous": "prevtrack",
                "prev": "prevtrack",
                "stop": "stop",
                "mute": "volumemute",
                "volume up": "volumeup",
                "volume down": "volumedown",
            }

            key = actions.get(action.lower())
            if key:
                pyautogui.press(key)
                return f"Media: {action}"
            else:
                return f"Unknown media action: {action}"
        except Exception as e:
            return f"Error controlling media: {e}"

    # ── Window Management ───────────────────────────────

    @staticmethod
    def manage_windows(action: str, window_title: str = None) -> str:
        """Manage windows: minimize, maximize, close, switch to."""
        try:
            import pyautogui

            if action == "minimize_all":
                pyautogui.hotkey("win", "d")
                return "Minimized all windows."
            elif action == "switch":
                pyautogui.hotkey("alt", "tab")
                return "Switched window."

            if window_title:
                try:
                    import pywinauto
                    from pywinauto import Desktop
                    desktop = Desktop(backend="uia")
                    windows = desktop.windows()
                    target = None
                    for w in windows:
                        if window_title.lower() in w.window_text().lower():
                            target = w
                            break

                    if target:
                        if action == "minimize":
                            target.minimize()
                            return f"Minimized {window_title}."
                        elif action == "maximize":
                            target.maximize()
                            return f"Maximized {window_title}."
                        elif action == "restore":
                            target.restore()
                            return f"Restored {window_title}."
                        elif action == "close":
                            target.close()
                            return f"Closed {window_title}."
                        elif action == "focus":
                            target.set_focus()
                            return f"Focused on {window_title}."
                    else:
                        return f"Window '{window_title}' not found."
                except ImportError:
                    return "pywinauto not available for window management."
            else:
                return "Please specify a window title."
        except Exception as e:
            return f"Error managing windows: {e}"
