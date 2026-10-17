@echo off
:: ─────────────────────────────────────────
:: JARVIS Auto-Start Setup
:: Adds JARVIS to Windows startup
:: ─────────────────────────────────────────

echo.
echo  ╔═══════════════════════════════════════╗
echo  ║     JARVIS Auto-Start Setup           ║
echo  ╚═══════════════════════════════════════╝
echo.

set JARVIS_DIR=%~dp0
set STARTUP_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup

:: Method 1: Create shortcut in Startup folder
echo Creating startup shortcut...

:: Create a VBScript to make a shortcut (Windows doesn't have a native shortcut creator)
set VBS_FILE=%TEMP%\create_shortcut.vbs
(
echo Set oWS = WScript.CreateObject^("WScript.Shell"^)
echo sLinkFile = "%STARTUP_DIR%\JARVIS.lnk"
echo Set oLink = oWS.CreateShortcut^(sLinkFile^)
echo oLink.TargetPath = "%JARVIS_DIR%start_jarvis.bat"
echo oLink.WorkingDirectory = "%JARVIS_DIR%"
echo oLink.Description = "JARVIS AI Assistant"
echo oLink.WindowStyle = 7
echo oLink.Save
) > "%VBS_FILE%"

cscript //nologo "%VBS_FILE%"
del "%VBS_FILE%"

if exist "%STARTUP_DIR%\JARVIS.lnk" (
    echo.
    echo  ✓ JARVIS will now start automatically when you log in!
    echo  Shortcut created at: %STARTUP_DIR%\JARVIS.lnk
) else (
    echo.
    echo  ✗ Failed to create startup shortcut.
    echo  You can manually add start_jarvis.bat to your Startup folder:
    echo  %STARTUP_DIR%
)

echo.
pause
