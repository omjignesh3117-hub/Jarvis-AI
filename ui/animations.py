"""
JARVIS UI Animations
Custom animation helpers and effects.
"""
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QTimer, QPoint, QSize
from PyQt6.QtWidgets import QWidget, QGraphicsOpacityEffect


def fade_in(widget: QWidget, duration: int = 400, delay: int = 0):
    """Fade in a widget."""
    effect = QGraphicsOpacityEffect(widget)
    widget.setGraphicsEffect(effect)
    effect.setOpacity(0)

    anim = QPropertyAnimation(effect, b"opacity")
    anim.setDuration(duration)
    anim.setStartValue(0.0)
    anim.setEndValue(1.0)
    anim.setEasingCurve(QEasingCurve.Type.OutCubic)

    if delay:
        QTimer.singleShot(delay, anim.start)
    else:
        anim.start()

    # Keep reference to prevent GC
    widget._fade_anim = anim
    return anim


def fade_out(widget: QWidget, duration: int = 300, delay: int = 0):
    """Fade out a widget."""
    effect = widget.graphicsEffect()
    if not isinstance(effect, QGraphicsOpacityEffect):
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)

    anim = QPropertyAnimation(effect, b"opacity")
    anim.setDuration(duration)
    anim.setStartValue(1.0)
    anim.setEndValue(0.0)
    anim.setEasingCurve(QEasingCurve.Type.InCubic)

    if delay:
        QTimer.singleShot(delay, anim.start)
    else:
        anim.start()

    widget._fade_anim = anim
    return anim


def slide_in_right(widget: QWidget, distance: int = 400, duration: int = 500):
    """Slide a widget in from the right."""
    start_pos = widget.pos() + QPoint(distance, 0)
    end_pos = widget.pos()

    widget.move(start_pos)
    widget.show()

    anim = QPropertyAnimation(widget, b"pos")
    anim.setDuration(duration)
    anim.setStartValue(start_pos)
    anim.setEndValue(end_pos)
    anim.setEasingCurve(QEasingCurve.Type.OutCubic)
    anim.start()

    widget._slide_anim = anim
    return anim


def slide_out_right(widget: QWidget, distance: int = 400, duration: int = 400):
    """Slide a widget out to the right."""
    start_pos = widget.pos()
    end_pos = widget.pos() + QPoint(distance, 0)

    anim = QPropertyAnimation(widget, b"pos")
    anim.setDuration(duration)
    anim.setStartValue(start_pos)
    anim.setEndValue(end_pos)
    anim.setEasingCurve(QEasingCurve.Type.InCubic)
    anim.finished.connect(widget.hide)
    anim.start()

    widget._slide_anim = anim
    return anim
