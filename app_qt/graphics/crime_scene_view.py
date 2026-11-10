"""Interactive 2D Crime Scene Canvas (QGraphicsView & QGraphicsScene) for PySide6 LOGIC COURTROOM.
Features procedural 2D room perspective, proximity forensic tool sweep (<75px),
custom tool reticles (Lens, UV Luminol, Dusting Powder), and direct evidence interactions.
"""

import math
from typing import Optional, List, Dict
from PySide6.QtCore import Qt, QTimer, Signal, QRectF, QPointF
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QRadialGradient
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsItem

from models.case import Case
from models.evidence import Evidence
from app_qt.config import (
    COLOR_GOLD, COLOR_GOLD_LIGHT, COLOR_WHITE, COLOR_ACCENT_GREEN,
    COLOR_ACCENT_RED, COLOR_ACCENT_BLUE
)
from app_qt.graphics.crime_scene_items import ClueHotspotItem
from app_qt.services.sound_service_qt import get_sound_service_qt


class CrimeSceneView(QGraphicsView):
    """Interactive 2D crime scene view with tool sweep detection and click selection."""

    evidence_clicked = Signal(object)        # (Evidence)
    evidence_double_clicked = Signal(object) # (Evidence)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene_obj = QGraphicsScene(0, 0, 705, 535, self)
        self.setScene(self.scene_obj)

        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setMouseTracking(True)
        self.setStyleSheet("background-color: #19120e; border: 1px solid #ffd741; border-radius: 8px;")

        self.case: Optional[Case] = None
        self.collected_ids: set[str] = set()
        self.inspected_ids: set[str] = set()
        self.selected_evidence: Optional[Evidence] = None
        self.active_tool: str = "MAGNIFIER"  # 'MAGNIFIER', 'LUMINOL', 'POWDER'

        self.mouse_scene_pos: QPointF = QPointF(-100, -100)
        self.cursor_inside = False
        self.anim_time: float = 0.0

        self.hotspot_items: Dict[str, ClueHotspotItem] = {}
        self.sound_service = get_sound_service_qt()

        # 50 FPS animation timer
        self.timer = QTimer(self)
        self.timer.setInterval(20)
        self.timer.timeout.connect(self._on_tick)
        self.timer.start()

    def set_case(self, case: Optional[Case], collected_ids: set[str], inspected_ids: set[str], selected_evidence: Optional[Evidence] = None):
        self.case = case
        self.collected_ids = set(collected_ids or [])
        self.inspected_ids = set(inspected_ids or [])
        self.selected_evidence = selected_evidence
        self._rebuild_scene()

    def set_tool(self, tool_name: str):
        self.active_tool = (tool_name or "MAGNIFIER").upper()
        self.viewport().update()

    def _rebuild_scene(self):
        self.scene_obj.clear()
        self.hotspot_items.clear()

        if not self.case:
            return

        for ev in self.case.evidence_list:
            is_col = ev.id in self.collected_ids
            is_insp = ev.id in self.inspected_ids
            item = ClueHotspotItem(ev, is_collected=is_col, is_inspected=is_insp)
            self.scene_obj.addItem(item)
            self.hotspot_items[ev.id] = item

        self.viewport().update()

    def mouseMoveEvent(self, event):
        self.cursor_inside = True
        self.mouse_scene_pos = self.mapToScene(event.pos())
        self._update_sweeps()
        self.viewport().update()
        super().mouseMoveEvent(event)

    def leaveEvent(self, event):
        self.cursor_inside = False
        self.mouse_scene_pos = QPointF(-100, -100)
        self._update_sweeps()
        self.viewport().update()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            item = self.itemAt(event.pos())
            if isinstance(item, ClueHotspotItem):
                self.selected_evidence = item.evidence
                self.sound_service.play("click")
                self.evidence_clicked.emit(item.evidence)
                self._update_sweeps()
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            item = self.itemAt(event.pos())
            if isinstance(item, ClueHotspotItem):
                self.evidence_double_clicked.emit(item.evidence)
        super().mouseDoubleClickEvent(event)

    def _update_sweeps(self):
        sweep_radius = 75.0
        for ev_id, item in self.hotspot_items.items():
            item_center = item.scenePos() + item.rect.center()
            dist = math.hypot(self.mouse_scene_pos.x() - item_center.x(),
                              self.mouse_scene_pos.y() - item_center.y())
            is_swept = self.cursor_inside and (dist < sweep_radius)
            is_col = ev_id in self.collected_ids
            is_insp = ev_id in self.inspected_ids
            is_sel = (self.selected_evidence is not None and self.selected_evidence.id == ev_id)

            item.update_state(
                is_collected=is_col,
                is_inspected=is_insp,
                is_selected=is_sel,
                is_swept=is_swept,
                active_tool=self.active_tool,
                anim_time=self.anim_time
            )

    def _on_tick(self):
        self.anim_time += 0.020
        if self.cursor_inside and self.isVisible():
            self._update_sweeps()
            self.viewport().update()

    def drawBackground(self, painter: QPainter, rect: QRectF):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = 705.0
        h = 535.0

        # 1. Wall Background
        painter.fillRect(QRectF(0, 0, w, h), QColor(28, 20, 16))

        # Vertical wall wood paneling lines
        painter.setPen(QPen(QColor(40, 30, 24), 1))
        for wx in range(0, int(w), 120):
            painter.drawLine(QPointF(wx, 0), QPointF(wx, h * 0.6))

        # 2. Window / Arch in background
        win_rect = QRectF(110, 35, 140, 150)
        painter.setBrush(QBrush(QColor(16, 22, 32)))
        painter.setPen(QPen(QColor(65, 48, 38), 3))
        painter.drawChord(win_rect, 0, 180 * 16)
        painter.drawLine(QPointF(win_rect.center().x(), win_rect.top()), QPointF(win_rect.center().x(), win_rect.bottom()))
        painter.drawLine(QPointF(win_rect.left(), win_rect.top() + 75), QPointF(win_rect.right(), win_rect.top() + 75))

        # 3. Floor Perspective
        floor_y = h * 0.6
        painter.setBrush(QBrush(QColor(36, 26, 20)))
        painter.setPen(QPen(QColor(60, 45, 35), 2))
        painter.drawRect(QRectF(0, floor_y, w, h - floor_y))

        # Perspective Floor Planks
        painter.setPen(QPen(QColor(30, 22, 17), 1))
        for px in range(0, int(w) + 100, 65):
            painter.drawLine(QPointF(px, floor_y), QPointF(px - 40, h))

    def drawForeground(self, painter: QPainter, rect: QRectF):
        """Draws tool overlays, UV dark wash, and tool cursor reticles."""
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = 705.0
        h = 535.0

        # 1. UV Luminol Dark Filter
        if self.active_tool == "LUMINOL":
            painter.fillRect(QRectF(0, 0, w, h), QColor(20, 10, 50, 130))

        # 2. Forensic Tool Cursor Reticle following mouse
        if self.cursor_inside and self.mouse_scene_pos.x() >= 0:
            mx = self.mouse_scene_pos.x()
            my = self.mouse_scene_pos.y()

            if self.active_tool == "LUMINOL":
                # Glowing UV spotlight cone
                grad = QRadialGradient(QPointF(mx, my), 85)
                grad.setColorAt(0.0, QColor(220, 255, 255, 160))
                grad.setColorAt(0.4, QColor(140, 220, 255, 90))
                grad.setColorAt(1.0, QColor(80, 120, 255, 0))
                painter.setPen(Qt.NoPen)
                painter.setBrush(QBrush(grad))
                painter.drawEllipse(QRectF(mx - 85, my - 85, 170, 170))
                painter.setPen(QPen(QColor(100, 200, 255), 1))
                painter.setBrush(Qt.NoBrush)
                painter.drawEllipse(QRectF(mx - 85, my - 85, 170, 170))

            elif self.active_tool == "POWDER":
                # Dusting Brush Reticle
                painter.setPen(QPen(QColor(220, 230, 245), 1))
                painter.setBrush(Qt.NoBrush)
                painter.drawEllipse(QRectF(mx - 30, my - 30, 60, 60))
                painter.drawEllipse(QRectF(mx - 10, my - 10, 20, 20))
                for i in range(4):
                    ang = (i / 4.0) * math.pi * 2.0 + (self.anim_time * 2.0)
                    dx = mx + math.cos(ang) * 34.0
                    dy = my + math.sin(ang) * 34.0
                    painter.setPen(Qt.NoPen)
                    painter.setBrush(QBrush(QColor(200, 215, 240)))
                    painter.drawEllipse(QRectF(dx - 2, dy - 2, 4, 4))

            else:
                # Magnifying Lens Reticle
                painter.setPen(QPen(COLOR_GOLD, 2))
                painter.setBrush(Qt.NoBrush)
                painter.drawEllipse(QRectF(mx - 44, my - 44, 88, 88))
                painter.setPen(QPen(COLOR_GOLD_LIGHT, 1))
                painter.drawEllipse(QRectF(mx - 40, my - 40, 80, 80))
                painter.drawLine(QPointF(mx - 12, my), QPointF(mx + 12, my))
                painter.drawLine(QPointF(mx, my - 12), QPointF(mx, my + 12))
                # Lens Handle
                painter.setPen(QPen(QColor(120, 75, 40), 6))
                painter.drawLine(QPointF(mx + 30, my + 30), QPointF(mx + 52, my + 52))

