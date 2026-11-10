"""Animated Royal Wax Seal Stamp Overlay for PySide6 LOGIC COURTROOM.
Falls onto the verdict report with bounce physics and radial shockwaves.
"""

from PySide6.QtCore import Qt, QTimer, QRectF, QPointF
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QFont
from PySide6.QtWidgets import QWidget

from app_qt.config import COLOR_GOLD, COLOR_GOLD_LIGHT, COLOR_WHITE, COLOR_ACCENT_RED
from app_qt.services.sound_service_qt import get_sound_service_qt


class WaxSealOverlay(QWidget):
    """Animated wax seal stamp dropped onto verdicts."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        self.text = "PROVEN"
        self.is_won = True
        self.y_pos = -120.0
        self.timer_val = 0.0
        self.duration = 2.2
        self.active = False
        self.sound_played = False

        self.sound_service = get_sound_service_qt()

        self.anim_timer = QTimer(self)
        self.anim_timer.setInterval(20)
        self.anim_timer.timeout.connect(self._on_tick)

        self.hide()

    def trigger(self, text: str = "PROVEN", is_won: bool = True):
        self.text = text
        self.is_won = is_won
        self.y_pos = -120.0
        self.timer_val = 0.0
        self.active = True
        self.sound_played = False

        if self.parent():
            self.setGeometry(0, 0, self.parent().width(), self.parent().height())
            self.raise_()

        self.show()
        self.anim_timer.start()

    def _on_tick(self):
        dt = 0.020
        self.timer_val += dt

        # Bounce fall animation in first 0.4 seconds
        if self.timer_val < 0.4:
            t = self.timer_val / 0.4
            # Ease out bounce approximation
            if t < (1.0 / 2.75):
                b = 7.5625 * t * t
            elif t < (2.0 / 2.75):
                t -= (1.5 / 2.75)
                b = 7.5625 * t * t + 0.75
            elif t < (2.5 / 2.75):
                t -= (2.25 / 2.75)
                b = 7.5625 * t * t + 0.9375
            else:
                t -= (2.625 / 2.75)
                b = 7.5625 * t * t + 0.984375

            self.y_pos = -120.0 + b * 220.0

            if t >= 0.9 and not self.sound_played:
                self.sound_played = True
                self.sound_service.play("gavel")
        else:
            self.y_pos = 100.0

        if self.timer_val >= self.duration:
            self.anim_timer.stop()
            # Remain visible on page until user dismisses screen

        self.update()

    def paintEvent(self, event):
        if not self.active:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        cx = self.width() / 2.0
        cy = float(self.y_pos)
        radius = 55.0

        # Wax Stamp Circle Body
        seal_color = QColor(175, 30, 25) if self.is_won else QColor(150, 105, 35)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(seal_color))
        painter.drawEllipse(QRectF(cx - radius, cy - radius, radius * 2, radius * 2))

        # Concentric Gold Filigree Rings
        painter.setPen(QPen(COLOR_GOLD, 2))
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(QRectF(cx - radius + 4, cy - radius + 4, (radius - 4) * 2, (radius - 4) * 2))
        painter.setPen(QPen(COLOR_GOLD_LIGHT, 1))
        painter.drawEllipse(QRectF(cx - radius + 9, cy - radius + 9, (radius - 9) * 2, (radius - 9) * 2))

        # Stamp Text
        painter.setFont(QFont("Segoe UI", 12, QFont.Bold))
        painter.setPen(QColor(255, 240, 180))
        stamp_label = "PROVEN" if self.is_won else "DISMISSED"
        painter.drawText(QRectF(cx - radius, cy - 14, radius * 2, 28), Qt.AlignCenter, stamp_label)

