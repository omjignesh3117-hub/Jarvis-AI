"""
JARVIS Tool Definitions
All functions exposed to Gemini for function calling.
"""


def get_tool_functions():
    """Return all tool function definitions for Gemini."""
    from core.system_controller import SystemController
    from core.app_controller import AppController

    return [
        # ── App Management ──
        open_application,
        close_application,

        # ── File Operations ──
        search_files,
        open_file,
        create_file,
        delete_file,

        # ── System Settings ──
        set_volume,
        set_brightness,
        lock_screen,
        shutdown_pc,
        toggle_wifi,

        # ── Process Management ──
        get_system_info,
        list_running_processes,
        kill_process,

        # ── Clipboard ──
        read_clipboard,
        write_clipboard,

        # ── Screenshots ──
        take_screenshot,

        # ── Web ──
        open_website,
        web_search,

        # ── Input ──
        send_keys,
        click_at_position,
        type_text,
        scroll_screen,

        # ── Window Management ──
        manage_windows,
        focus_window,
        list_open_windows,

        # ── Media ──
        control_media,

        # ── Utility ──
        get_current_time,
        run_shell_command,
    ]


# ═══════════════════════════════════════════════
# Tool function wrappers with proper docstrings
# Gemini uses these docstrings to understand tools
# ═══════════════════════════════════════════════

def open_application(app_name: str) -> str:
    """Open an application by its common name.
    Examples: 'chrome', 'notepad', 'spotify', 'vs code', 'file explorer', 'calculator', 'settings'.
    You can also pass the executable name directly like 'winword.exe'.

    Args:
        app_name: The name of the application to open.
    """
    from core.system_controller import SystemController
    return SystemController.open_application(app_name)


def close_application(app_name: str) -> str:
    """Close a currently running application by name.

    Args:
        app_name: The name of the application to close (e.g., 'chrome', 'notepad').
    """
    from core.system_controller import SystemController
    return SystemController.close_application(app_name)


def search_files(query: str, directory: str = None, max_results: int = 10) -> str:
    """Search for files by name pattern on the computer.

    Args:
        query: The filename pattern to search for (partial match supported).
        directory: Optional directory to search in. Defaults to user's home directory.
        max_results: Maximum number of results to return. Default 10.
    """
    from core.system_controller import SystemController
    return SystemController.search_files(query, directory, max_results)


def open_file(file_path: str) -> str:
    """Open a file with its default application.

    Args:
        file_path: Full path to the file to open.
    """
    from core.system_controller import SystemController
    return SystemController.open_file(file_path)


def create_file(file_path: str, content: str = "") -> str:
    """Create a new file at the specified path with optional content.

    Args:
        file_path: Full path where the file should be created.
        content: Text content to write to the file.
    """
    from core.system_controller import SystemController
    return SystemController.create_file(file_path, content)


def delete_file(file_path: str) -> str:
    """Delete a file or folder. WARNING: This permanently deletes the file.

    Args:
        file_path: Full path to the file or folder to delete.
    """
    from core.system_controller import SystemController
    return SystemController.delete_file(file_path)


def set_volume(level: int) -> str:
    """Set the system volume level.

    Args:
        level: Volume level from 0 (mute) to 100 (maximum).
    """
    from core.system_controller import SystemController
    return SystemController.set_volume(level)


def set_brightness(level: int) -> str:
    """Set the screen brightness level.

    Args:
        level: Brightness level from 0 (dimmest) to 100 (brightest).
    """
    from core.system_controller import SystemController
    return SystemController.set_brightness(level)


def lock_screen() -> str:
    """Lock the computer screen immediately."""
    from core.system_controller import SystemController
    return SystemController.lock_screen()


def shutdown_pc(action: str = "shutdown") -> str:
    """Shutdown, restart, or put the computer to sleep.

    Args:
        action: One of 'shutdown', 'restart', 'sleep', or 'cancel'.
    """
    from core.system_controller import SystemController
    return SystemController.shutdown_pc(action)


def toggle_wifi(enable: bool = True) -> str:
    """Enable or disable WiFi.

    Args:
        enable: True to enable WiFi, False to disable it.
    """
    from core.system_controller import SystemController
    return SystemController.toggle_wifi(enable)


def get_system_info() -> str:
    """Get current system resource usage including CPU, RAM, disk, and battery status."""
    from core.system_controller import SystemController
    return SystemController.get_system_info()


def list_running_processes(top_n: int = 15) -> str:
    """List the top running processes sorted by memory usage.

    Args:
        top_n: Number of top processes to show. Default 15.
    """
    from core.system_controller import SystemController
    return SystemController.list_running_processes(top_n)


def kill_process(process_name: str) -> str:
    """Force kill a running process by name.

    Args:
        process_name: Name of the process to kill (e.g., 'chrome.exe').
    """
    from core.system_controller import SystemController
    return SystemController.kill_process(process_name)


def read_clipboard() -> str:
    """Read the current text content from the clipboard."""
    from core.system_controller import SystemController
    return SystemController.read_clipboard()


def write_clipboard(text: str) -> str:
    """Copy text to the clipboard.

    Args:
        text: The text to copy to clipboard.
    """
    from core.system_controller import SystemController
    return SystemController.write_clipboard(text)


def take_screenshot(save_path: str = None) -> str:
    """Capture a screenshot and save it to disk.

    Args:
        save_path: Optional file path to save the screenshot. Defaults to Desktop.
    """
    from core.system_controller import SystemController
    return SystemController.take_screenshot(save_path)


def open_website(url: str) -> str:
    """Open a website URL in the default browser.

    Args:
        url: The URL to open (e.g., 'google.com' or 'https://youtube.com').
    """
    from core.system_controller import SystemController
    return SystemController.open_website(url)


def web_search(query: str) -> str:
    """Search Google for a query in the default browser.

    Args:
        query: The search query string.
    """
    from core.system_controller import SystemController
    return SystemController.web_search(query)


def send_keys(keys: str) -> str:
    """Send keyboard input. For hotkeys use '+' separator like 'ctrl+c', 'alt+f4', 'win+e'.
    For single keys use the key name like 'enter', 'tab', 'escape'.
    For regular text, just pass the text string.

    Args:
        keys: The keys to press or text to type.
    """
    from core.app_controller import AppController
    return AppController.send_keys(keys)


def click_at_position(x: int, y: int, button: str = "left", clicks: int = 1) -> str:
    """Click the mouse at specific screen coordinates.

    Args:
        x: X coordinate on screen.
        y: Y coordinate on screen.
        button: Mouse button - 'left', 'right', or 'middle'.
        clicks: Number of clicks (1 for single, 2 for double click).
    """
    from core.app_controller import AppController
    return AppController.click_at(x, y, button, clicks)


def type_text(text: str) -> str:
    """Type text at the current cursor position. Supports unicode characters.

    Args:
        text: The text to type.
    """
    from core.app_controller import AppController
    return AppController.type_text(text)


def scroll_screen(amount: int) -> str:
    """Scroll the screen up or down.

    Args:
        amount: Positive number to scroll up, negative to scroll down.
    """
    from core.app_controller import AppController
    return AppController.scroll(amount)


def manage_windows(action: str, window_title: str = None) -> str:
    """Manage desktop windows. Actions: minimize, maximize, restore, close, focus, minimize_all, switch.

    Args:
        action: The window action to perform.
        window_title: Optional title of the target window (not needed for minimize_all or switch).
    """
    from core.system_controller import SystemController
    return SystemController.manage_windows(action, window_title)


def focus_window(title: str) -> str:
    """Bring a specific window to the foreground.

    Args:
        title: Part of the window title to search for.
    """
    from core.app_controller import AppController
    return AppController.focus_window(title)


def list_open_windows() -> str:
    """List all currently open/visible windows on the desktop."""
    from core.app_controller import AppController
    return AppController.list_windows()


def control_media(action: str) -> str:
    """Control media playback. Actions: play, pause, next, previous, stop, mute, volume up, volume down.

    Args:
        action: The media action to perform.
    """
    from core.system_controller import SystemController
    return SystemController.control_media(action)


def get_current_time() -> str:
    """Get the current date and time."""
    from core.system_controller import SystemController
    return SystemController.get_current_time()


def run_shell_command(command: str) -> str:
    """Execute a shell/terminal command and return the output.
    Use this for any system command like 'ipconfig', 'dir', 'ping', etc.

    Args:
        command: The shell command to execute.
    """
    from core.system_controller import SystemController
    return SystemController.run_shell_command(command)
