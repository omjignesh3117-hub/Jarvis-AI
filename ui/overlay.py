"""
JARVIS Desktop Overlay
Main transparent overlay window with orb and chat panel.
"""
import logging
import sys

from PyQt6.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout,
    QSystemTrayIcon, QMenu, QLabel
)
from PyQt6.QtCore import (
    Qt, QTimer, pyqtSignal, pyqtSlot, QPoint, QSize
)
from PyQt6.QtGui import (
    QIcon, QFont, QAction, QPixmap, QPainter, QColor,
    QRadialGradient, QCursor
)

from ui.orb_widget import OrbWidget
from ui.chat_panel import ChatPanel
from ui.styles import OVERLAY_STYLE

logger = logging.getLogger("jarvis.ui")


class JarvisOverlay(QWidget):
    """Main desktop overlay — transparent, always-on-top widget."""

    # Signals for thread-safe UI updates
    state_changed = pyqtSignal(str)
    response_received = pyqtSignal(str)
    action_received = pyqtSignal(str)
    user_command = pyqtSignal(str)

    def __init__(self, config):
        super().__init__()
        self.config = config
        self._dragging = False
        self._drag_pos = QPoint()

        self._setup_window()
        self._setup_ui()
        self._setup_tray()
        self._connect_signals()

        logger.info("Overlay initialized.")

    def _setup_window(self):
        """Configure window properties."""
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Tool  # Don't show in taskbar
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        # Position based on config
        screen = QApplication.primaryScreen()
        if screen:
            geo = screen.availableGeometry()
            if self.config.ORB_POSITION == "bottom-right":
                x = geo.right() - 500
                y = geo.bottom() - 600
            elif self.config.ORB_POSITION == "bottom-center":
                x = geo.center().x() - 250
                y = geo.bottom() - 600
            else:  # bottom-left
                x = geo.left() + 20
                y = geo.bottom() - 600

            self.setGeometry(x, y, 500, 580)

    def _setup_ui(self):
        """Build the overlay interface."""
        self.setStyleSheet(OVERLAY_STYLE)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── Chat panel (left side, hidden by default) ──
        self._chat = ChatPanel(self)
        self._chat.hide()
        main_layout.addWidget(self._chat, stretch=1)

        # ── Orb column (right side) ──
        orb_layout = QVBoxLayout()
        orb_layout.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)

        # Status text above orb
        self._status_text = QLabel("")
        self._status_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._status_text.setFont(QFont("Segoe UI", 9))
        self._status_text.setStyleSheet(
            "color: #00D4FF; background: transparent; padding: 4px;"
        )
        self._status_text.hide()

        # The orb
        self._orb = OrbWidget(self.config.ORB_SIZE, self)
        self._orb.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self._orb.mousePressEvent = self._orb_clicked

        orb_layout.addStretch()
        orb_layout.addWidget(self._status_text, alignment=Qt.AlignmentFlag.AlignCenter)
        orb_layout.addWidget(self._orb, alignment=Qt.AlignmentFlag.AlignCenter)
        orb_layout.addSpacing(10)

        main_layout.addLayout(orb_layout)

    def _setup_tray(self):
        """Create system tray icon and context menu."""
        # Create a simple icon using Qt drawing
        pixmap = QPixmap(64, 64)
        pixmap.fill(QColor(0, 0, 0, 0))

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        gradient = QRadialGradient(32, 32, 28)
        gradient.setColorAt(0, QColor(0, 212, 255))
        gradient.setColorAt(1, QColor(0, 100, 180))
        painter.setBrush(gradient)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(4, 4, 56, 56)
        painter.end()

        icon = QIcon(pixmap)

        self._tray = QSystemTrayIcon(icon, self)
        self._tray.setToolTip("JARVIS AI Assistant")

        menu = QMenu()
        menu.setStyleSheet("""
            QMenu {
                background: #111827;
                color: #E2E8F0;
                border: 1px solid #1E293B;
                padding: 4px;
            }
            QMenu::item:selected {
                background: #1E293B;
            }
        """)

        show_action = menu.addAction("Show/Hide JARVIS")
        show_action.triggered.connect(self._toggle_visibility)

        chat_action = menu.addAction("Toggle Chat")
        chat_action.triggered.connect(self._toggle_chat)

        menu.addSeparator()

        quit_action = menu.addAction("Quit JARVIS")
        quit_action.triggered.connect(self._quit)

        self._tray.setContextMenu(menu)
        self._tray.activated.connect(self._tray_activated)
        self._tray.show()

    def _connect_signals(self):
        """Connect thread-safe signals."""
        self.state_changed.connect(self._on_state_changed)
        self.response_received.connect(self._on_response)
        self.action_received.connect(self._on_action)
        self._chat.message_sent.connect(self._on_chat_message)
        self._chat.mic_clicked.connect(self._on_mic_click)

    # ── Public API ──

    def set_state(self, state: str):
        """Thread-safe state update."""
        self.state_changed.emit(state)

    def show_response(self, text: str):
        """Thread-safe response display."""
        self.response_received.emit(text)

    def show_action(self, text: str):
        """Thread-safe action display."""
        self.action_received.emit(text)

    def add_user_message(self, text: str):
        """Add user message to chat."""
        self._chat.add_message(text, is_user=True)
        if not self._chat.is_visible:
            self._chat.show_panel()

    # ── Signal Handlers ──

    @pyqtSlot(str)
    def _on_state_changed(self, state: str):
        """Handle state change on main thread."""
        self._orb.set_state(state)
        self._chat.set_status(state)

        if state == "listening":
            self._status_text.setText("Listening...")
            self._status_text.show()
        elif state == "processing":
            self._status_text.setText("Processing...")
            self._status_text.show()
        elif state == "speaking":
            self._status_text.setText("Speaking...")
            self._status_text.show()
        else:
            self._status_text.hide()

    @pyqtSlot(str)
    def _on_response(self, text: str):
        """Handle AI response on main thread."""
        self._chat.add_message(text, is_user=False)
        if not self._chat.is_visible:
            self._chat.show_panel()

    @pyqtSlot(str)
    def _on_action(self, text: str):
        """Handle action notification."""
        self._status_text.setText(text)
        self._status_text.show()

    def _on_chat_message(self, text: str):
        """Handle typed message from chat panel."""
        self.user_command.emit(text)

    def _on_mic_click(self):
        """Handle mic button click."""
        self.user_command.emit("__MIC_TRIGGER__")

    # ── Interaction ──

    def _orb_clicked(self, event):
        """Handle orb click — toggle chat panel."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._toggle_chat()
        elif event.button() == Qt.MouseButton.RightButton:
            # Force listen
            self.user_command.emit("__MIC_TRIGGER__")

    def _toggle_chat(self):
        """Toggle the chat panel."""
        self._chat.toggle()

    def _toggle_visibility(self):
        """Toggle overlay visibility."""
        if self.isVisible():
            self.hide()
        else:
            self.show()

    def _tray_activated(self, reason):
        """Handle tray icon interactions."""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self._toggle_visibility()
        elif reason == QSystemTrayIcon.ActivationReason.Trigger:
            self._toggle_chat()

    def _quit(self):
        """Quit the application."""
        self._tray.hide()
        QApplication.quit()

    # ── Window dragging ──

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self._dragging and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, event):
        self._dragging = False
