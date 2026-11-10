"""Interactive Clue Hotspot Graphics Items for PySide6 LOGIC COURTROOM.
Manages hidden state, proximity sweep illumination, rotating shimmer stars, and inspection markers.
"""

import math
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QFont
from PySide6.QtWidgets import QGraphicsItem

from models.evidence import Evidence
from app_qt.config import (
    COLOR_GOLD, COLOR_GOLD_LIGHT, COLOR_WHITE, COLOR_ACCENT_GREEN,
    COLOR_ACCENT_RED, COLOR_ACCENT_BLUE
)


class ClueHotspotItem(QGraphicsItem):
    """Interactive forensic clue item in the Crime Scene QGraphicsScene."""

    def __init__(self, evidence: Evidence, is_collected: bool = False, is_inspected: bool = False):
        super().__init__()
        self.evidence = evidence
        self.is_collected = is_collected
        self.is_inspected = is_inspected
        self.is_swept = False
        self.is_selected = False
        self.active_tool = "MAGNIFIER"
        self.anim_time = 0.0

        x, y, w, h = evidence.scene_pos
        w = max(45.0, min(160.0, float(w)))
        h = max(45.0, min(130.0, float(h)))
        # Clamp within standard 705x535 viewport bounds
        clamped_x = max(20.0, min(680.0 - w, float(x)))
        clamped_y = max(20.0, min(510.0 - h, float(y)))

        self.setPos(clamped_x, clamped_y)
        self.rect = QRectF(0, 0, w, h)

        self.setAcceptHoverEvents(True)
        self.setCursor(Qt.PointingHandCursor)

    def boundingRect(self) -> QRectF:
        # Extra margin for glow and label tag
        return self.rect.adjusted(-12, -22, 12, 24)

    def update_state(self, is_collected: bool, is_inspected: bool, is_selected: bool, is_swept: bool, active_tool: str, anim_time: float):
        changed = (
            self.is_collected != is_collected or
            self.is_inspected != is_inspected or
            self.is_selected != is_selected or
            self.is_swept != is_swept or
            self.active_tool != active_tool or
            self.is_swept  # Continuously repaint shimmer when swept
        )
        self.is_collected = is_collected
        self.is_inspected = is_inspected
        self.is_selected = is_selected
        self.is_swept = is_swept
        self.active_tool = active_tool
        self.anim_time = anim_time
        if changed:
            self.update()

    def paint(self, painter: QPainter, option, widget=None):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 1. If Clue is Collected or Inspected -> Draw Permanent Forensic Token
        if self.is_collected or self.is_inspected:
            bg_col = QColor(35, 55, 38, 170) if self.is_collected else QColor(48, 38, 28, 170)
            bdr_col = COLOR_ACCENT_GREEN if self.is_collected else (COLOR_GOLD if self.is_selected else QColor(160, 120, 60))

            painter.setPen(QPen(bdr_col, 2 if self.is_selected else 1))
            painter.setBrush(QBrush(bg_col))
            painter.drawRoundedRect(self.rect, 6, 6)

            # Draw Category Icon
            self._draw_icon(painter, self.rect)

            # Label Tag
            lbl_txt = f"✓ {self.evidence.name}" if self.is_collected else f"🔍 {self.evidence.name}"
            painter.setFont(QFont("Segoe UI", 8, QFont.Bold))
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(QColor(18, 12, 10, 220)))

            tag_rect = QRectF(self.rect.left(), self.rect.bottom() + 2, self.rect.width(), 16)
            painter.drawRoundedRect(tag_rect, 3, 3)
            painter.setPen(COLOR_WHITE)
            painter.drawText(tag_rect, Qt.AlignCenter, lbl_txt[:18])

        # 2. If Clue is Currently Swept by Active Forensic Tool -> Reveal with Glow & Shimmer
        elif self.is_swept:
            pulse = (math.sin(self.anim_time * 6.0) + 1.0) * 0.5

            if self.active_tool == "LUMINOL":
                glow_col = QColor(100, 255, 230)
            elif self.active_tool == "POWDER":
                glow_col = QColor(210, 230, 255)
            else:
                glow_col = COLOR_GOLD_LIGHT

            glow_alpha = int(140 + pulse * 100)
            glow_col.setAlpha(glow_alpha)

            # Pulsing selection border
            painter.setPen(QPen(glow_col, 2, Qt.DashLine if self.active_tool == "POWDER" else Qt.SolidLine))
            painter.setBrush(QBrush(QColor(glow_col.red(), glow_col.green(), glow_col.blue(), 40)))
            painter.drawRoundedRect(self.rect, 8, 8)

            # Shimmer star particles rotating around center
            cx = self.rect.center().x()
            cy = self.rect.center().y()
            for k in range(3):
                sang = (k / 3.0) * math.pi * 2.0 + (self.anim_time * 4.0)
                sx = cx + math.cos(sang) * (self.rect.width() / 2.8)
                sy = cy + math.sin(sang) * (self.rect.height() / 2.8)
                painter.setPen(Qt.NoPen)
                painter.setBrush(QBrush(glow_col))
                painter.drawEllipse(QRectF(sx - 3, sy - 3, 6, 6))

            # Reveal Prompt Tag
            painter.setFont(QFont("Segoe UI", 8, QFont.Bold))
            painter.setPen(glow_col)
            painter.drawText(QRectF(self.rect.left() - 10, self.rect.top() - 18, self.rect.width() + 20, 16),
                             Qt.AlignCenter, "★ CLUE DETECTED! [CLICK]")

        # 3. Otherwise: Completely invisible in crime scene room
        else:
            pass

    def _draw_icon(self, painter: QPainter, rect: QRectF):
        icon = self.evidence.icon_type.lower()
        cx = rect.center().x()
        cy = rect.center().y() - 2

        painter.setPen(QPen(COLOR_GOLD, 2))
        painter.setBrush(Qt.NoBrush)

        if icon == "knife":
            painter.drawLine(QPointF(cx - 12, cy - 8), QPointF(cx + 8, cy + 6))
            painter.setPen(QPen(COLOR_ACCENT_RED, 3))
            painter.drawPoint(QPointF(cx + 10, cy + 7))
        elif icon == "phone":
            painter.drawRoundedRect(QRectF(cx - 8, cy - 12, 16, 24), 2, 2)
            painter.drawLine(QPointF(cx - 4, cy + 8), QPointF(cx + 4, cy + 8))
        elif icon == "fingerprint":
            painter.drawArc(QRectF(cx - 10, cy - 12, 20, 24), 0, 180 * 16)
            painter.drawArc(QRectF(cx - 6, cy - 8, 12, 18), 0, 180 * 16)
        elif icon == "glass":
            painter.drawLine(QPointF(cx - 8, cy + 8), QPointF(cx, cy - 10))
            painter.drawLine(QPointF(cx, cy - 10), QPointF(cx + 8, cy + 8))
        elif icon == "cctv":
            painter.drawRect(QRectF(cx - 10, cy - 6, 18, 12))
            painter.setPen(QPen(COLOR_ACCENT_RED, 2))
            painter.drawPoint(QPointF(cx + 5, cy - 2))
        elif icon == "safe":
            painter.drawRect(QRectF(cx - 10, cy - 10, 20, 20))
            painter.drawEllipse(QRectF(cx - 4, cy - 4, 8, 8))
        elif icon == "blood":
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(COLOR_ACCENT_RED))
            painter.drawEllipse(QRectF(cx - 6, cy - 4, 12, 12))
        else:
            # Magnifier generic
            painter.drawEllipse(QRectF(cx - 8, cy - 8, 14, 14))
            painter.drawLine(QPointF(cx + 4, cy + 4), QPointF(cx + 10, cy + 10))

