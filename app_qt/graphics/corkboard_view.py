"""Interactive Detective Corkboard Canvas (QGraphicsView & QGraphicsScene) for PySide6 LOGIC COURTROOM.
Visualizes suspects, forensic ties, and contradictions with draggable pins and colored yarn links.
"""

from typing import Optional, List, Dict
from PySide6.QtCore import Qt, QRectF, QPointF, Signal
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QFont
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene

from models.case import Case
from app_qt.config import COLOR_GOLD, COLOR_GOLD_LIGHT, COLOR_WHITE
from app_qt.graphics.corkboard_items import CorkNodeItem, YarnLinkItem
from app_qt.services.sound_service_qt import get_sound_service_qt


class CorkboardView(QGraphicsView):
    """Interactive corkboard canvas with connected yarn links."""

    node_selected = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene_obj = QGraphicsScene(0, 0, 1000, 480, self)
        self.setScene(self.scene_obj)
        self.scene_obj.selectionChanged.connect(self._on_selection_changed)

        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setStyleSheet("background-color: #24160f; border: 2px solid #704222; border-radius: 8px;")

        self.case: Optional[Case] = None
        self.filter_mode = "ALL"
        self.nodes: Dict[str, CorkNodeItem] = {}
        self.yarns: List[YarnLinkItem] = []
        self.sound_service = get_sound_service_qt()

    def set_case(self, case: Optional[Case], filter_mode: str = "ALL"):
        self.case = case
        self.filter_mode = filter_mode
        self._populate_board()

    def set_filter(self, filter_mode: str):
        self.filter_mode = filter_mode
        for y in self.yarns:
            if filter_mode == "ALL":
                y.setVisible(True)
            elif filter_mode == "CONFIRMED":
                y.setVisible(y.link_type == "confirmed")
            elif filter_mode == "CONTRADICTIONS":
                y.setVisible(y.link_type == "contradiction")
        self.viewport().update()

    def _populate_board(self):
        self.scene_obj.clear()
        self.nodes.clear()
        self.yarns.clear()

        if not self.case:
            return

        # 1. Place Suspect Nodes on Left Column
        for i, s in enumerate(self.case.suspects):
            node = CorkNodeItem(
                node_id=s.id,
                title=f"{s.name}\n({s.occupation})",
                category="suspect",
                x=40.0,
                y=35.0 + i * 115.0,
                w=165.0,
                h=72.0
            )
            self.scene_obj.addItem(node)
            self.nodes[s.id] = node

        # 2. Place Evidence Nodes in Middle & Right Columns
        col_x = [270.0, 520.0, 770.0]
        for idx, ev in enumerate(self.case.evidence_list):
            c_idx = idx % 3
            r_idx = idx // 3
            node = CorkNodeItem(
                node_id=ev.id,
                title=f"{ev.name}\nRel: {int(ev.reliability * 100)}%",
                category="evidence",
                x=col_x[c_idx],
                y=35.0 + r_idx * 115.0,
                w=160.0,
                h=70.0
            )
            self.scene_obj.addItem(node)
            self.nodes[ev.id] = node

        # 3. Add Contradiction Nodes if suspects have contradictions
        cont_count = 0
        for s in self.case.suspects:
            for cont_text in s.contradictions:
                cont_id = f"CONT_{s.id}_{cont_count}"
                node = CorkNodeItem(
                    node_id=cont_id,
                    title=f"⚡ {cont_text[:34]}...",
                    category="contradiction",
                    x=520.0,
                    y=265.0 + cont_count * 85.0,
                    w=190.0,
                    h=65.0
                )
                self.scene_obj.addItem(node)
                self.nodes[cont_id] = node

                # Yarn to suspect
                if s.id in self.nodes:
                    yarn = YarnLinkItem(self.nodes[s.id], node, link_type="contradiction")
                    self.scene_obj.addItem(yarn)
                    self.yarns.append(yarn)

                cont_count += 1

        # 4. Link evidence items with their associated suspects
        for ev in self.case.evidence_list:
            if ev.associated_suspect and ev.associated_suspect in self.nodes and ev.id in self.nodes:
                yarn = YarnLinkItem(self.nodes[ev.associated_suspect], self.nodes[ev.id], link_type="confirmed")
                self.scene_obj.addItem(yarn)
                self.yarns.append(yarn)

        self.set_filter(self.filter_mode)

    def _on_selection_changed(self):
        selected = self.scene_obj.selectedItems()
        for item in selected:
            if isinstance(item, CorkNodeItem):
                self.node_selected.emit(item)
                return

    def drawBackground(self, painter: QPainter, rect: QRectF):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Realistic warm corkboard texture
        painter.fillRect(rect, QColor(48, 30, 18))

        # Cork grain speckles
        painter.setPen(QPen(QColor(38, 22, 13), 1))
        step = 28
        for x in range(int(rect.left()), int(rect.right()), step):
            for y in range(int(rect.top()), int(rect.bottom()), step):
                off_x = (x * 13 + y * 7) % 11
                off_y = (x * 7 + y * 13) % 11
                painter.drawPoint(QPointF(x + off_x, y + off_y))

        # Wooden border frame trim
        painter.setPen(QPen(QColor(85, 52, 30), 4))
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(QRectF(2, 2, 996, 476))
        painter.setPen(QPen(COLOR_GOLD, 1))
        painter.drawRect(QRectF(6, 6, 988, 468))
