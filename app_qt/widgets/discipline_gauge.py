"""Animated ECG Credibility Heartbeat Gauge Widget for PySide6 LOGIC COURTROOM.
Displays real-time pulsing ECG waveform and 3 judicial warning strike pips.
"""

import math
from PySide6.QtCore import Qt, QTimer, QRectF, QPointF
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QPolygonF
from PySide6.QtWidgets import QWidget

from app_qt.config import (
    COLOR_BG_PANEL, COLOR_GOLD, COLOR_GOLD_LIGHT, COLOR_WHITE,
    COLOR_ACCENT_RED, COLOR_ACCENT_GREEN
)


class DisciplineGaugeQt(QWidget):
    """Pulsating ECG monitor with courtroom strike pips."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(165, 52)

        self.strikes: int = 0
        self.credibility_pct: float = 100.0
        self.time: float = 0.0
        self.pulse_phase: float = 0.0

        self.timer = QTimer(self)
        self.timer.setInterval(30)  # ~33 FPS
        self.timer.timeout.connect(self._on_tick)
        self.timer.start()

    def set_strikes(self, count: int):
        self.strikes = max(0, min(3, int(count)))
        self.update()

    def set_credibility(self, pct: float):
        self.credibility_pct = max(0.0, min(100.0, float(pct)))

    def _on_tick(self):
        dt = 0.030
        self.time += dt
        speed = 2.0 + (1.0 - (self.credibility_pct / 100.0)) * 4.0
        self.pulse_phase = (self.pulse_phase + dt * speed) % 1.0
        if self.isVisible():
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        is_danger = self.strikes >= 2

        # 1. Background Panel with Chamfered Trim
        panel_rect = QRectF(2, 2, w - 4, h - 4)
        bdr_col = COLOR_ACCENT_RED if is_danger else COLOR_GOLD
        painter.setPen(QPen(bdr_col, 1))
        painter.setBrush(QBrush(QColor(24, 14, 12)))
        painter.drawRoundedRect(panel_rect, 6, 6)

        # 2. Header Label
        lbl_col = QColor(255, 120, 100) if is_danger else COLOR_GOLD_LIGHT
        painter.setFont(QFont("Segoe UI", 8, QFont.Bold))
        painter.setPen(lbl_col)
        painter.drawText(QRectF(8, 4, w - 16, 14), Qt.AlignLeft, "COURT DISCIPLINE")

        # 3. ECG Waveform in middle
        wave_pts = []
        wave_w = int(w - 16)
        wave_y = 23.0
        for i in range(0, wave_w, 3):
            rel_x = i / float(wave_w)
            dist = abs(rel_x - self.pulse_phase)
            if dist < 0.08:
                spike = math.sin((dist / 0.08) * math.pi) * 6.0
            else:
                spike = math.sin(self.time * 6.0 + i) * 1.0
            wave_pts.append(QPointF(8 + i, wave_y - spike))

        wave_col = QColor(255, 80, 70) if is_danger else COLOR_ACCENT_GREEN
        painter.setPen(QPen(wave_col, 1.5))
        for j in range(len(wave_pts) - 1):
            painter.drawLine(wave_pts[j], wave_pts[j + 1])

        # 4. Three Warning Strike Pips at bottom
        for i in range(3):
            pip_x = 24.0 + i * 44.0
            pip_y = 39.0
            is_struck = (i < self.strikes)

            pip_bg = COLOR_ACCENT_RED if is_struck else QColor(50, 35, 26)
            pip_bdr = QColor(255, 120, 120) if is_struck else COLOR_GOLD

            painter.setPen(QPen(pip_bdr, 1))
            painter.setBrush(QBrush(pip_bg))
            painter.drawEllipse(QRectF(pip_x - 7, pip_y - 7, 14, 14))

            # Pip label
            painter.setFont(QFont("Segoe UI", 7, QFont.Bold))
            painter.setPen(COLOR_WHITE if is_struck else QColor(180, 165, 150))
            painter.drawText(QRectF(pip_x - 7, pip_y - 7, 14, 14), Qt.AlignCenter, "!" if is_struck else f"#{i+1}")

