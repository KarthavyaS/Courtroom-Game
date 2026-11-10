"""Animated Suspect Dock Platform Widget for PySide6 LOGIC COURTROOM.
Draws an illuminated circular dock with pulsating gold energy rings, rotating runes,
and a brass suspect nameplate.
"""

import math
from PySide6.QtCore import Qt, QTimer, QRectF, QPointF
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QFont
from PySide6.QtWidgets import QWidget

from app_qt.config import (
    COLOR_GOLD, COLOR_GOLD_LIGHT, COLOR_GOLD_DARK, COLOR_WHITE,
    COLOR_ACCENT_RED
)


class SuspectDockQt(QWidget):
    """Accused suspect dock platform with glowing gold perimeter."""

    def __init__(self, suspect_name: str = "The Accused", parent=None):
        super().__init__(parent)
        self.setFixedSize(160, 75)

        self.suspect_name = suspect_name
        self.anim_time = 0.0

        self.timer = QTimer(self)
        self.timer.setInterval(30)
        self.timer.timeout.connect(self._on_tick)
        self.timer.start()

    def set_suspect_name(self, name: str):
        self.suspect_name = name or "The Accused"
        self.update()

    def _on_tick(self):
        self.anim_time += 0.030
        if self.isVisible():
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        cx = self.width() / 2.0
        cy = 28.0
        rx = 62.0
        ry = 20.0

        # 1. Base Shadow
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(10, 6, 4)))
        painter.drawEllipse(QRectF(cx - rx - 4, cy - ry + 4, (rx + 4) * 2, (ry + 4) * 2))

        # 2. Wooden Platform Floor
        painter.setBrush(QBrush(QColor(45, 28, 18)))
        painter.setPen(QPen(COLOR_GOLD_DARK, 1))
        painter.drawEllipse(QRectF(cx - rx, cy - ry, rx * 2, ry * 2))

        # 3. Pulsating Glow Ring
        pulse = (math.sin(self.anim_time * 3.0) + 1.0) * 0.5
        glow_alpha = int(80 + pulse * 140)
        glow_pen = QPen(QColor(255, 215, 65, glow_alpha), 2)
        painter.setPen(glow_pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(QRectF(cx - rx + 3, cy - ry + 2, (rx - 3) * 2, (ry - 2) * 2))

        # 4. Rotating Runes / Compass dots
        angle_offset = self.anim_time * 0.8
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(COLOR_GOLD_LIGHT))
        for i in range(6):
            theta = angle_offset + i * (math.pi / 3.0)
            px = cx + (rx - 5.0) * math.cos(theta)
            py = cy + (ry - 3.0) * math.sin(theta)
            painter.drawEllipse(QRectF(px - 2, py - 2, 4, 4))

        # 5. Brass Suspect Nameplate
        plate_w = 146.0
        plate_h = 22.0
        plate_x = cx - plate_w / 2.0
        plate_y = cy + ry + 4.0

        painter.setPen(QPen(COLOR_GOLD, 1))
        painter.setBrush(QBrush(QColor(32, 20, 14)))
        painter.drawRoundedRect(QRectF(plate_x, plate_y, plate_w, plate_h), 4, 4)

        # Status badge "[ACCUSED]"
        painter.setFont(QFont("Segoe UI", 7, QFont.Bold))
        painter.setPen(COLOR_ACCENT_RED)
        painter.drawText(QRectF(plate_x + 6, plate_y + 2, 55, 18), Qt.AlignLeft | Qt.AlignVCenter, "[ACCUSED]")

        # Suspect Name
        painter.setFont(QFont("Segoe UI", 8, QFont.Bold))
        painter.setPen(COLOR_WHITE)
        painter.drawText(QRectF(plate_x + 62, plate_y + 2, 80, 18), Qt.AlignLeft | Qt.AlignVCenter, self.suspect_name[:14])

