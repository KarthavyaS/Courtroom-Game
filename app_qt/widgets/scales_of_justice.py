"""Animated Golden Scales of Justice Widget for PySide6 LOGIC COURTROOM.
Tilts dynamically based on Jury Persuasion (0% to 100%) with swinging pans.
"""

import math
from PySide6.QtCore import Qt, QTimer, QRectF, QPointF
from PySide6.QtGui import QPainter, QColor, QPen, QBrush
from PySide6.QtWidgets import QWidget

from app_qt.config import COLOR_GOLD, COLOR_GOLD_LIGHT, COLOR_GOLD_DARK


class ScalesOfJusticeQt(QWidget):
    """Swaying and tilting golden scales reflecting courtroom persuasion."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(140, 60)

        self.jury_persuasion = 50.0  # 0 to 100
        self.current_tilt = 0.0
        self.time = 0.0

        self.timer = QTimer(self)
        self.timer.setInterval(25)  # 40 FPS
        self.timer.timeout.connect(self._on_tick)
        self.timer.start()

    def set_persuasion(self, value: float):
        self.jury_persuasion = max(0.0, min(100.0, float(value)))

    def _on_tick(self):
        dt = 0.025
        self.time += dt
        target_tilt = (self.jury_persuasion - 50.0) / 50.0
        self.current_tilt += (target_tilt - self.current_tilt) * min(1.0, 5.0 * dt)
        if self.isVisible():
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        cx = self.width() / 2.0
        cy = 14.0
        bar_len = 45.0

        tilt_angle = self.current_tilt * 0.28 + math.sin(self.time * 1.5) * 0.03

        # 1. Central Pillar & Stand
        painter.setPen(QPen(COLOR_GOLD_DARK, 3))
        painter.drawLine(QPointF(cx, cy), QPointF(cx, cy + 38))
        painter.setBrush(QBrush(COLOR_GOLD_LIGHT))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QRectF(cx - 4, cy - 4, 8, 8))
        painter.drawRoundedRect(QRectF(cx - 16, cy + 34, 32, 6), 2, 2)

        # 2. Tilting Crossbar
        dx = math.cos(tilt_angle) * bar_len
        dy = math.sin(tilt_angle) * bar_len
        left_end = QPointF(cx - dx, cy - dy)
        right_end = QPointF(cx + dx, cy + dy)

        painter.setPen(QPen(COLOR_GOLD, 3))
        painter.drawLine(left_end, right_end)

        # 3. Hanging Scale Pans
        for pt, is_left in [(left_end, True), (right_end, False)]:
            phase = 0.0 if is_left else math.pi
            pan_drop = 22.0 + math.sin(self.time * 2.0 + phase) * 2.5
            pan_center = QPointF(pt.x(), pt.y() + pan_drop)

            # Strings
            painter.setPen(QPen(COLOR_GOLD_DARK, 1))
            painter.drawLine(pt, QPointF(pan_center.x() - 10, pan_center.y()))
            painter.drawLine(pt, QPointF(pan_center.x() + 10, pan_center.y()))

            # Pan Curve
            painter.setPen(QPen(COLOR_GOLD_LIGHT, 2))
            painter.drawArc(QRectF(pan_center.x() - 12, pan_center.y() - 3, 24, 8), 0, 180 * 16)

