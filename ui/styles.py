"""
JARVIS UI Styles
Premium dark theme inspired by Iron Man's HUD.
"""

# Color Palette
COLORS = {
    "bg_dark": "#0A0E17",
    "bg_panel": "#111827",
    "bg_surface": "#1E293B",
    "bg_hover": "#253349",
    "accent": "#00D4FF",
    "accent_glow": "#0088CC",
    "accent_dim": "#004466",
    "accent_secondary": "#00FF88",
    "warning": "#FFB800",
    "error": "#FF4444",
    "text_primary": "#E2E8F0",
    "text_secondary": "#94A3B8",
    "text_dim": "#64748B",
    "border": "#1E293B",
    "border_active": "#00D4FF",
}

# Main overlay stylesheet
OVERLAY_STYLE = """
QWidget {
    font-family: 'Segoe UI', 'Inter', sans-serif;
    color: #E2E8F0;
}
"""

# Chat panel stylesheet
CHAT_PANEL_STYLE = """
QWidget#chatPanel {
    background-color: rgba(10, 14, 23, 220);
    border: 1px solid rgba(0, 212, 255, 0.3);
    border-radius: 16px;
}

QScrollArea {
    border: none;
    background: transparent;
}

QScrollBar:vertical {
    width: 6px;
    background: transparent;
    margin: 4px 0;
}

QScrollBar::handle:vertical {
    background: rgba(0, 212, 255, 0.4);
    border-radius: 3px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background: rgba(0, 212, 255, 0.7);
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none;
}
"""

# Message bubble styles
USER_BUBBLE_STYLE = """
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(0, 136, 204, 0.3),
        stop:1 rgba(0, 68, 102, 0.3));
    border: 1px solid rgba(0, 212, 255, 0.3);
    border-radius: 12px;
    padding: 10px 14px;
    color: #E2E8F0;
    font-size: 13px;
"""

ASSISTANT_BUBBLE_STYLE = """
    background: rgba(30, 41, 59, 0.8);
    border: 1px solid rgba(0, 212, 255, 0.15);
    border-radius: 12px;
    padding: 10px 14px;
    color: #E2E8F0;
    font-size: 13px;
"""

STATUS_LABEL_STYLE = """
    color: {color};
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
    padding: 4px 12px;
    background: rgba(0, 0, 0, 0.3);
    border-radius: 10px;
"""

# Input bar style
INPUT_STYLE = """
QLineEdit {
    background: rgba(17, 24, 39, 0.9);
    border: 1px solid rgba(0, 212, 255, 0.3);
    border-radius: 20px;
    padding: 8px 16px;
    color: #E2E8F0;
    font-size: 13px;
    selection-background-color: rgba(0, 212, 255, 0.3);
}
QLineEdit:focus {
    border: 1px solid rgba(0, 212, 255, 0.7);
}
QLineEdit::placeholder {
    color: #64748B;
}
"""

# Button style
SEND_BUTTON_STYLE = """
QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #0088CC, stop:1 #00D4FF);
    border: none;
    border-radius: 18px;
    color: white;
    font-size: 14px;
    font-weight: bold;
    padding: 6px;
    min-width: 36px;
    min-height: 36px;
}
QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #00AAEE, stop:1 #00E4FF);
}
QPushButton:pressed {
    background: #0066AA;
}
"""

MIC_BUTTON_STYLE = """
QPushButton {{
    background: rgba({bg_r}, {bg_g}, {bg_b}, 0.3);
    border: 2px solid rgba({bg_r}, {bg_g}, {bg_b}, 0.5);
    border-radius: 18px;
    color: white;
    font-size: 16px;
    min-width: 36px;
    min-height: 36px;
}}
QPushButton:hover {{
    background: rgba({bg_r}, {bg_g}, {bg_b}, 0.5);
    border: 2px solid rgba({bg_r}, {bg_g}, {bg_b}, 0.8);
}}
"""
