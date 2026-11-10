"""Corkboard Pin Cards and Curved Yarn Link Items for PySide6 LOGIC COURTROOM.
"""

import math
from typing import Optional, List
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QPainterPath
from PySide6.QtWidgets import QGraphicsItem, QGraphicsPathItem

from app_qt.config import (
    COLOR_GOLD, COLOR_GOLD_LIGHT, COLOR_GOLD_DARK, COLOR_WHITE,
    COLOR_ACCENT_RED, COLOR_ACCENT_BLUE, COLOR_ACCENT_GREEN
)


class CorkNodeItem(QGraphicsItem):
    """Draggable parchment pin card on the detective corkboard."""

    def __init__(self, node_id: str, title: str, category: str, x: float, y: float, w: float = 145.0, h: float = 68.0):
        super().__init__()
        self.node_id = node_id
        self.title = title
        self.category = (category or "evidence").lower()
        self.w = w
        self.h = h

        self.setPos(x, y)
        self.rect = QRectF(0, 0, w, h)

        self.setFlags(
            QGraphicsItem.ItemIsMovable |
            QGraphicsItem.ItemIsSelectable |
            QGraphicsItem.ItemSendsGeometryChanges
        )
        self.setCursor(Qt.OpenHandCursor)
        self.connected_yarns: List["YarnLinkItem"] = []

    def boundingRect(self) -> QRectF:
        return self.rect.adjusted(-6, -10, 6, 6)

    def get_pin_center(self) -> QPointF:
        """Returns the world coordinates of the top brass pushpin."""
        return self.scenePos() + QPointF(self.w / 2.0, 6.0)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            for y in self.connected_yarns:
                y.update_path()
        return super().itemChange(change, value)

    def mousePressEvent(self, event):
        self.setCursor(Qt.ClosedHandCursor)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.setCursor(Qt.OpenHandCursor)
        super().mouseReleaseEvent(event)

    def paint(self, painter: QPainter, option, widget=None):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 1. Parchment Card Shadow
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(15, 10, 8, 140)))
        painter.drawRoundedRect(self.rect.adjusted(2, 3, 2, 3), 6, 6)

        # 2. Parchment Card Body
        bg_col = QColor(40, 26, 18)
        bdr_col = COLOR_GOLD if self.isSelected() else QColor(130, 95, 60)

        if self.category == "contradiction":
            bdr_col = COLOR_ACCENT_RED
            bg_col = QColor(48, 20, 18)
        elif self.category == "suspect":
            bdr_col = COLOR_GOLD_LIGHT
            bg_col = QColor(36, 32, 45)
        elif self.category == "timeline":
            bdr_col = COLOR_ACCENT_BLUE

        painter.setPen(QPen(bdr_col, 2 if self.isSelected() else 1))
        painter.setBrush(QBrush(bg_col))
        painter.drawRoundedRect(self.rect, 6, 6)

        # Inner fillet
        painter.setPen(QPen(QColor(255, 255, 255, 20), 1))
        painter.drawRoundedRect(self.rect.adjusted(3, 3, -3, -3), 4, 4)

        # 3. Category Tag
        tag_text = f"[{self.category.upper()}]"
        painter.setFont(QFont("Segoe UI", 7, QFont.Bold))
        tag_col = COLOR_ACCENT_RED if self.category == "contradiction" else (COLOR_ACCENT_BLUE if self.category == "timeline" else COLOR_GOLD)
        painter.setPen(tag_col)
        painter.drawText(QRectF(8, 12, self.w - 16, 14), Qt.AlignLeft, tag_text)

        # 4. Title Text
        painter.setFont(QFont("Segoe UI", 9, QFont.Bold))
        painter.setPen(COLOR_WHITE)
        painter.drawText(QRectF(8, 28, self.w - 16, self.h - 32), Qt.AlignLeft | Qt.TextWordWrap, self.title)

        # 5. Top Brass Pushpin
        pin_cx = self.w / 2.0
        pin_cy = 6.0
        # Pin shadow
        painter.setBrush(QBrush(QColor(10, 8, 6, 160)))
        painter.drawEllipse(QRectF(pin_cx - 4, pin_cy, 8, 8))
        # Pin body (Gold/Brass)
        painter.setPen(QPen(COLOR_GOLD_DARK, 1))
        painter.setBrush(QBrush(COLOR_GOLD_LIGHT))
        painter.drawEllipse(QRectF(pin_cx - 5, pin_cy - 5, 10, 10))
        painter.setBrush(QBrush(COLOR_WHITE))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QRectF(pin_cx - 2, pin_cy - 4, 3, 3))


class YarnLinkItem(QGraphicsPathItem):
    """Quadratic Bézier colored yarn line connecting two pushpins with physical gravity sag."""

    def __init__(self, node_a: CorkNodeItem, node_b: CorkNodeItem, link_type: str = "confirmed"):
        super().__init__()
        self.node_a = node_a
        self.node_b = node_b
        self.link_type = link_type.lower()

        node_a.connected_yarns.append(self)
        node_b.connected_yarns.append(self)

        self.setZValue(-1)  # Behind cards

        if self.link_type == "contradiction":
            self.yarn_color = COLOR_ACCENT_RED
        elif self.link_type == "timeline":
            self.yarn_color = COLOR_ACCENT_BLUE
        else:
            self.yarn_color = COLOR_GOLD

        self.update_path()

    def update_path(self):
        p1 = self.node_a.get_pin_center()
        p2 = self.node_b.get_pin_center()

        # Midpoint with gravity sag
        mid_x = (p1.x() + p2.x()) / 2.0
        dist = math.hypot(p2.x() - p1.x(), p2.y() - p1.y())
        sag = min(45.0, max(12.0, dist * 0.12))
        mid_y = max(p1.y(), p2.y()) + sag

        path = QPainterPath()
        path.moveTo(p1)
        path.quadTo(QPointF(mid_x, mid_y), p2)

        self.setPath(path)
        self.setPen(QPen(self.yarn_color, 2.5, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
