"""
JARVIS Animated Orb Widget
A glowing, pulsing orb that serves as the primary visual indicator.
"""
import math
import time
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QTimer, QPointF, QRectF
from PyQt6.QtGui import (
    QPainter, QRadialGradient, QColor, QPen,
    QBrush, QPainterPath, QLinearGradient
)


class OrbWidget(QWidget):
    """Animated glowing orb — the visual heart of JARVIS.

    States:
        idle       - Gentle pulse, dim glow
        listening  - Bright pulse, expanding rings
        processing - Spinning arc animation
        speaking   - Waveform ripple effect
        error      - Red pulse
    """

    def __init__(self, size=80, parent=None):
        super().__init__(parent)
        self.setFixedSize(size + 40, size + 40)  # Extra space for glow
        self._size = size
        self._state = "idle"
        self._time = 0
        self._pulse_phase = 0
        self._ring_phase = 0
        self._spin_angle = 0
        self._wave_data = [0] * 20
        self._wave_idx = 0

        # Colors for each state
        self._colors = {
            "idle": (QColor(0, 180, 255), QColor(0, 100, 180)),
            "listening": (QColor(0, 255, 200), QColor(0, 180, 140)),
            "processing": (QColor(0, 212, 255), QColor(0, 100, 200)),
            "speaking": (QColor(0, 230, 255), QColor(0, 150, 200)),
            "error": (QColor(255, 80, 80), QColor(180, 40, 40)),
        }

        # Animation timer — 60fps
        self._timer = QTimer()
        self._timer.timeout.connect(self._tick)
        self._timer.start(16)  # ~60fps

    def set_state(self, state: str):
        """Change the orb state."""
        self._state = state
        self._ring_phase = 0
        self.update()

    @property
    def state(self):
        return self._state

    def _tick(self):
        """Animation tick."""
        self._time += 0.016
        self._pulse_phase += 0.04
        self._ring_phase += 0.03
        self._spin_angle += 3

        if self._state == "speaking":
            # Simulate waveform
            import random
            self._wave_data[self._wave_idx % len(self._wave_data)] = random.uniform(0.3, 1.0)
            self._wave_idx += 1

        self.update()

    def paintEvent(self, event):
        """Custom paint — draws the animated orb."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        cx, cy = w / 2, h / 2
        r = self._size / 2

        color_bright, color_dark = self._colors.get(
            self._state, self._colors["idle"]
        )

        # ── Outer glow ──
        pulse = 0.5 + 0.5 * math.sin(self._pulse_phase)
        glow_size = r + 15 + pulse * 8

        glow_gradient = QRadialGradient(cx, cy, glow_size)
        glow_color = QColor(color_bright)
        glow_color.setAlpha(int(40 + pulse * 30))
        glow_gradient.setColorAt(0.0, glow_color)
        glow_color.setAlpha(0)
        glow_gradient.setColorAt(1.0, glow_color)

        painter.setBrush(QBrush(glow_gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(cx, cy), glow_size, glow_size)

        # ── State-specific effects ──
        if self._state == "listening":
            self._draw_listening_rings(painter, cx, cy, r, color_bright)
        elif self._state == "processing":
            self._draw_processing_arc(painter, cx, cy, r, color_bright)
        elif self._state == "speaking":
            self._draw_speaking_waves(painter, cx, cy, r, color_bright)

        # ── Core orb ──
        core_gradient = QRadialGradient(cx - r * 0.2, cy - r * 0.2, r * 1.2)
        core_gradient.setColorAt(0.0, color_bright)
        core_gradient.setColorAt(0.5, color_dark)
        bg = QColor(10, 14, 23)
        bg.setAlpha(200)
        core_gradient.setColorAt(1.0, bg)

        painter.setBrush(QBrush(core_gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(cx, cy), r * 0.6, r * 0.6)

        # ── Inner bright spot ──
        inner_gradient = QRadialGradient(cx - r * 0.1, cy - r * 0.1, r * 0.3)
        spot_color = QColor(255, 255, 255, int(120 + pulse * 60))
        inner_gradient.setColorAt(0.0, spot_color)
        spot_color.setAlpha(0)
        inner_gradient.setColorAt(1.0, spot_color)

        painter.setBrush(QBrush(inner_gradient))
        painter.drawEllipse(QPointF(cx, cy), r * 0.3, r * 0.3)

        # ── Outer ring ──
        ring_pen = QPen(QColor(color_bright))
        ring_pen.setWidth(2)
        ring_alpha = int(100 + pulse * 80)
        ring_color = QColor(color_bright)
        ring_color.setAlpha(ring_alpha)
        ring_pen.setColor(ring_color)
        painter.setPen(ring_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QPointF(cx, cy), r * 0.65, r * 0.65)

        painter.end()

    def _draw_listening_rings(self, painter, cx, cy, r, color):
        """Draw expanding rings when listening."""
        for i in range(3):
            phase = self._ring_phase + i * 1.2
            ring_r = r * 0.7 + (phase % 3) * r * 0.4
            alpha = max(0, 150 - int((phase % 3) * 80))
            c = QColor(color)
            c.setAlpha(alpha)
            pen = QPen(c)
            pen.setWidth(2)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(QPointF(cx, cy), ring_r, ring_r)

    def _draw_processing_arc(self, painter, cx, cy, r, color):
        """Draw spinning arc when processing."""
        arc_r = r * 0.8
        c = QColor(color)
        c.setAlpha(180)
        pen = QPen(c)
        pen.setWidth(3)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        rect = QRectF(cx - arc_r, cy - arc_r, arc_r * 2, arc_r * 2)
        painter.drawArc(rect, int(self._spin_angle * 16), 120 * 16)
        painter.drawArc(rect, int((self._spin_angle + 180) * 16), 80 * 16)

    def _draw_speaking_waves(self, painter, cx, cy, r, color):
        """Draw waveform visualization when speaking."""
        n = len(self._wave_data)
        for i in range(n):
            angle = (i / n) * 2 * math.pi
            amplitude = self._wave_data[i] * r * 0.3
            inner_r = r * 0.7
            outer_r = inner_r + amplitude

            x1 = cx + inner_r * math.cos(angle)
            y1 = cy + inner_r * math.sin(angle)
            x2 = cx + outer_r * math.cos(angle)
            y2 = cy + outer_r * math.sin(angle)

            c = QColor(color)
            c.setAlpha(int(150 + self._wave_data[i] * 100))
            pen = QPen(c)
            pen.setWidth(3)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))

        # Decay wave data
        self._wave_data = [max(0, v - 0.03) for v in self._wave_data]

    def enterEvent(self, event):
        """Mouse hover effect."""
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        super().enterEvent(event)
