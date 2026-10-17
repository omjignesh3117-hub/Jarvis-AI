"""
JARVIS Chat Panel
Slide-out conversation panel with message bubbles.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QLineEdit, QPushButton, QFrame,
    QSizePolicy, QGraphicsOpacityEffect
)
from PyQt6.QtCore import (
    Qt, QPropertyAnimation, QEasingCurve, QSize,
    pyqtSignal, QTimer, QParallelAnimationGroup
)
from PyQt6.QtGui import QFont, QColor, QIcon

from ui.styles import (
    CHAT_PANEL_STYLE, USER_BUBBLE_STYLE, ASSISTANT_BUBBLE_STYLE,
    STATUS_LABEL_STYLE, INPUT_STYLE, SEND_BUTTON_STYLE, MIC_BUTTON_STYLE
)


class MessageBubble(QFrame):
    """Single chat message bubble."""

    def __init__(self, text: str, is_user: bool = True, parent=None):
        super().__init__(parent)
        self.setObjectName("messageBubble")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 2, 0, 2)

        # Role label
        role = QLabel("You" if is_user else "JARVIS")
        role.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        role.setStyleSheet(
            f"color: {'#00D4FF' if not is_user else '#94A3B8'}; "
            "background: transparent; border: none; padding: 0;"
        )

        # Message text
        msg = QLabel(text)
        msg.setWordWrap(True)
        msg.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        msg.setFont(QFont("Segoe UI", 10))
        msg.setStyleSheet(
            USER_BUBBLE_STYLE if is_user else ASSISTANT_BUBBLE_STYLE
        )
        msg.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)

        # Align user messages right, assistant left
        if is_user:
            role.setAlignment(Qt.AlignmentFlag.AlignRight)
            layout.addWidget(role)
            layout.addWidget(msg)
        else:
            role.setAlignment(Qt.AlignmentFlag.AlignLeft)
            layout.addWidget(role)
            layout.addWidget(msg)

        # Fade-in animation
        self._opacity = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self._opacity)
        self._opacity.setOpacity(0)

        self._fade_anim = QPropertyAnimation(self._opacity, b"opacity")
        self._fade_anim.setDuration(300)
        self._fade_anim.setStartValue(0.0)
        self._fade_anim.setEndValue(1.0)
        self._fade_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        QTimer.singleShot(50, self._fade_anim.start)


class ChatPanel(QWidget):
    """Slide-out chat panel with conversation history and input."""

    message_sent = pyqtSignal(str)  # Emitted when user sends a message
    mic_clicked = pyqtSignal()       # Emitted when mic button is pressed

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("chatPanel")
        self.setFixedWidth(380)
        self.setStyleSheet(CHAT_PANEL_STYLE)

        self._visible = False
        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(8)

        # ── Header ──
        header = QHBoxLayout()

        title = QLabel("J.A.R.V.I.S.")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #00D4FF; background: transparent; border: none;")

        self._status_label = QLabel("● IDLE")
        self._status_label.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self._update_status_style("idle")

        header.addWidget(title)
        header.addStretch()
        header.addWidget(self._status_label)
        main_layout.addLayout(header)

        # ── Separator ──
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background: rgba(0, 212, 255, 0.2); max-height: 1px; border: none;")
        main_layout.addWidget(sep)

        # ── Chat scroll area ──
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setStyleSheet("background: transparent; border: none;")

        self._chat_container = QWidget()
        self._chat_container.setStyleSheet("background: transparent;")
        self._chat_layout = QVBoxLayout(self._chat_container)
        self._chat_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._chat_layout.setSpacing(8)
        self._chat_layout.setContentsMargins(4, 4, 4, 4)

        self._scroll.setWidget(self._chat_container)
        main_layout.addWidget(self._scroll, stretch=1)

        # ── Input bar ──
        input_layout = QHBoxLayout()
        input_layout.setSpacing(6)

        # Mic button
        self._mic_btn = QPushButton("🎤")
        self._mic_btn.setFixedSize(36, 36)
        self._mic_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._mic_btn.setStyleSheet(
            MIC_BUTTON_STYLE.format(bg_r=0, bg_g=212, bg_b=255)
        )
        self._mic_btn.clicked.connect(self.mic_clicked.emit)

        # Text input
        self._input = QLineEdit()
        self._input.setPlaceholderText("Type a command...")
        self._input.setStyleSheet(INPUT_STYLE)
        self._input.returnPressed.connect(self._send_message)

        # Send button
        self._send_btn = QPushButton("→")
        self._send_btn.setFixedSize(36, 36)
        self._send_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._send_btn.setStyleSheet(SEND_BUTTON_STYLE)
        self._send_btn.clicked.connect(self._send_message)

        input_layout.addWidget(self._mic_btn)
        input_layout.addWidget(self._input, stretch=1)
        input_layout.addWidget(self._send_btn)
        main_layout.addLayout(input_layout)

    def add_message(self, text: str, is_user: bool = True):
        """Add a message bubble to the chat."""
        bubble = MessageBubble(text, is_user, self._chat_container)
        self._chat_layout.addWidget(bubble)

        # Auto-scroll to bottom
        QTimer.singleShot(100, self._scroll_to_bottom)

    def set_status(self, state: str):
        """Update the status indicator."""
        states = {
            "idle": "● ONLINE",
            "listening": "◉ LISTENING",
            "processing": "◎ PROCESSING",
            "speaking": "◉ SPEAKING",
            "error": "✕ ERROR",
        }
        self._status_label.setText(states.get(state, "● ONLINE"))
        self._update_status_style(state)

    def _update_status_style(self, state: str):
        """Update status label color based on state."""
        colors = {
            "idle": "#00D4FF",
            "listening": "#00FF88",
            "processing": "#FFB800",
            "speaking": "#00D4FF",
            "error": "#FF4444",
        }
        color = colors.get(state, "#00D4FF")
        self._status_label.setStyleSheet(STATUS_LABEL_STYLE.format(color=color))

    def toggle(self):
        """Toggle chat panel visibility."""
        self._visible = not self._visible
        self.setVisible(self._visible)

    def show_panel(self):
        self._visible = True
        self.setVisible(True)

    def hide_panel(self):
        self._visible = False
        self.setVisible(False)

    @property
    def is_visible(self):
        return self._visible

    def _send_message(self):
        """Send the typed message."""
        text = self._input.text().strip()
        if text:
            self._input.clear()
            self.message_sent.emit(text)

    def _scroll_to_bottom(self):
        """Scroll chat to the latest message."""
        scrollbar = self._scroll.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
