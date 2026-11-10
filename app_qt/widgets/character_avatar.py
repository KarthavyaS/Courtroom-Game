"""Animated Vector Character Avatar Widget for PySide6 LOGIC COURTROOM.
Draws characters (Judge, Lawyer, Heir, Partner, Butler, Doctor) with procedural
breathing, blinking, speaking mouth modulation, emotional expressions, and pointing poses.
"""

import math
import random
from PySide6.QtCore import Qt, QTimer, QRectF, QPointF
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QPolygonF, QFont
from PySide6.QtWidgets import QWidget

from app_qt.config import (
    COLOR_BG_PANEL, COLOR_GOLD, COLOR_WHITE, COLOR_MUTED_TEXT,
    COLOR_ACCENT_RED, COLOR_ACCENT_BLUE, COLOR_ACCENT_GREEN
)


class CharacterAvatarQt(QWidget):
    """Renders an interactive animated character avatar."""

    def __init__(self, character_type: str = "heir", name: str = "Unknown", parent=None):
        super().__init__(parent)
        self.character_type = character_type.lower()
        self.name = name
        self.expression = "neutral"  # neutral, angry, nervous, surprised, thinking, satisfied, speaking, breakdown, pointing
        self.is_speaking = False

        self.anim_time = random.uniform(0.0, 10.0)
        self.blink_timer = random.uniform(2.0, 4.5)
        self.is_blinking = False

        self.setMinimumSize(95, 100)

        # Internal animation timer
        self.timer = QTimer(self)
        self.timer.setInterval(20)  # 50 FPS
        self.timer.timeout.connect(self._on_tick)
        self.timer.start()

    def set_expression(self, expression: str, is_speaking: bool = False):
        self.expression = (expression or "neutral").lower()
        self.is_speaking = is_speaking
        self.update()

    def set_character(self, character_type: str, name: str = ""):
        self.character_type = (character_type or "heir").lower()
        if name:
            self.name = name
        self.update()

    def _on_tick(self):
        dt = 0.020
        self.anim_time += dt
        self.blink_timer -= dt

        if self.blink_timer <= 0:
            self.is_blinking = True
            if self.blink_timer <= -0.16:
                self.is_blinking = False
                self.blink_timer = random.uniform(2.5, 5.0)

        if self.isVisible():
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()

        # 1. Outer Frame with Gold Trim
        frame_rect = QRectF(2, 2, w - 4, h - 4)
        painter.setPen(QPen(COLOR_GOLD, 2))
        painter.setBrush(QBrush(QColor(38, 22, 14)))
        painter.drawRoundedRect(frame_rect, 10, 10)

        cx = w / 2.0
        cy = h / 2.0

        # Jitter / Tremble for nervous or breakdown
        if self.expression in ["nervous", "breakdown"]:
            mag = 2.0 if self.expression == "breakdown" else 0.8
            cx += random.uniform(-mag, mag)
            cy += random.uniform(-mag, mag)

        # Subtle breathing idle wave
        breath = math.sin(self.anim_time * 2.5) * 1.5
        cy += breath

        # 2. Clothing & Shoulders
        self._draw_clothing(painter, cx, cy)

        # 3. Head & Skin
        face_color = QColor(235, 195, 165)
        if self.expression in ["angry", "breakdown"]:
            face_color = QColor(245, 175, 155)  # Flushed red
        elif self.expression == "nervous":
            face_color = QColor(225, 200, 180)  # Pale

        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(face_color))
        painter.drawEllipse(QRectF(cx - 20, cy - 25, 40, 45))

        # 4. Hair Styles
        self._draw_hair(painter, cx, cy)

        # 5. Eyebrows
        self._draw_eyebrows(painter, cx, cy)

        # 6. Eyes (with blinking & darting pupils)
        self._draw_eyes(painter, cx, cy)

        # 7. Mouth (with talking animation)
        self._draw_mouth(painter, cx, cy)

        # 8. Overlays: Spectacles, Sweat drops, Anger marks
        self._draw_overlays(painter, cx, cy, w, h)

    def _draw_clothing(self, painter: QPainter, cx: float, cy: float):
        if self.character_type in ["judge"]:
            # Judicial Robe & White Jabot Collar
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(QColor(20, 18, 18)))
            painter.drawEllipse(QRectF(cx - 44, cy + 12, 88, 55))
            painter.setBrush(QBrush(COLOR_WHITE))
            poly = QPolygonF([QPointF(cx - 14, cy + 15), QPointF(cx + 14, cy + 15), QPointF(cx, cy + 34)])
            painter.drawPolygon(poly)
        elif self.character_type in ["lawyer", "counsel", "counsel_1", "heir"]:
            # Navy Tailored Coat & Tie
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(QColor(30, 50, 75)))
            painter.drawEllipse(QRectF(cx - 44, cy + 12, 88, 55))
            painter.setBrush(QBrush(COLOR_WHITE))
            poly = QPolygonF([QPointF(cx - 12, cy + 15), QPointF(cx + 12, cy + 15), QPointF(cx, cy + 30)])
            painter.drawPolygon(poly)
            painter.setBrush(QBrush(COLOR_ACCENT_RED))
            tie = QPolygonF([QPointF(cx - 4, cy + 18), QPointF(cx + 4, cy + 18), QPointF(cx, cy + 30)])
            painter.drawPolygon(tie)

            # Pointing arm pose during objections
            if self.expression in ["pointing", "objection"]:
                painter.setBrush(QBrush(QColor(30, 50, 75)))
                arm = QPolygonF([QPointF(cx + 25, cy + 15), QPointF(cx + 45, cy - 2), QPointF(cx + 42, cy + 12)])
                painter.drawPolygon(arm)
                painter.setPen(QPen(QColor(235, 195, 165), 3))
                painter.drawLine(QPointF(cx + 45, cy - 2), QPointF(cx + 56, cy - 8))
                painter.setPen(Qt.NoPen)
        elif self.character_type in ["partner", "socialite", "counsel_2"]:
            # Emerald Silk Dress
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(QColor(25, 70, 50)))
            painter.drawEllipse(QRectF(cx - 44, cy + 12, 88, 55))
            painter.setPen(QPen(COLOR_GOLD, 2))
            painter.drawArc(QRectF(cx - 16, cy + 16, 32, 16), 0, 180 * 16)
        elif self.character_type in ["butler", "staff", "counsel_3"]:
            # Waistcoat & Bowtie
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(QColor(30, 30, 35)))
            painter.drawEllipse(QRectF(cx - 44, cy + 12, 88, 55))
            painter.setBrush(QBrush(COLOR_WHITE))
            poly = QPolygonF([QPointF(cx - 14, cy + 15), QPointF(cx + 14, cy + 15), QPointF(cx, cy + 32)])
            painter.drawPolygon(poly)
            painter.setBrush(QBrush(QColor(10, 10, 10)))
            bow = QPolygonF([QPointF(cx - 7, cy + 18), QPointF(cx + 7, cy + 18), QPointF(cx, cy + 22)])
            painter.drawPolygon(bow)
        else:
            # Doctor / Executive Tweed Vest
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(QColor(70, 65, 60)))
            painter.drawEllipse(QRectF(cx - 44, cy + 12, 88, 55))
            painter.setBrush(QBrush(COLOR_WHITE))
            poly = QPolygonF([QPointF(cx - 12, cy + 15), QPointF(cx + 12, cy + 15), QPointF(cx, cy + 30)])
            painter.drawPolygon(poly)

    def _draw_hair(self, painter: QPainter, cx: float, cy: float):
        painter.setPen(Qt.NoPen)
        if self.character_type == "judge":
            wig_color = QColor(232, 232, 238)
            painter.setBrush(QBrush(wig_color))
            painter.drawEllipse(QRectF(cx - 28, cy - 44, 56, 38))
            painter.drawEllipse(QRectF(cx - 33, cy - 24, 18, 18))
            painter.drawEllipse(QRectF(cx + 15, cy - 24, 18, 18))
        elif self.character_type in ["partner", "socialite", "counsel_2"]:
            hair_col = QColor(165, 95, 45)
            painter.setBrush(QBrush(hair_col))
            painter.drawEllipse(QRectF(cx - 18, cy - 40, 36, 26))
            painter.drawEllipse(QRectF(cx - 24, cy - 28, 48, 24))
        elif self.character_type in ["butler", "staff"]:
            painter.setBrush(QBrush(QColor(150, 150, 155)))
            painter.drawEllipse(QRectF(cx - 24, cy - 28, 48, 16))
        else:
            # Slicked gentleman brown hair
            painter.setBrush(QBrush(QColor(50, 30, 15)))
            painter.drawChord(QRectF(cx - 22, cy - 35, 44, 25), 0, 180 * 16)
            painter.drawEllipse(QRectF(cx - 22, cy - 24, 10, 10))

    def _draw_eyebrows(self, painter: QPainter, cx: float, cy: float):
        eye_y = cy - 8
        painter.setPen(QPen(QColor(70, 40, 30), 2))
        if self.expression in ["angry", "breakdown"]:
            painter.drawLine(QPointF(cx - 15, eye_y - 8), QPointF(cx - 4, eye_y - 4))
            painter.drawLine(QPointF(cx + 15, eye_y - 8), QPointF(cx + 4, eye_y - 4))
        elif self.expression == "surprised":
            painter.drawArc(QRectF(cx - 16, eye_y - 14, 12, 8), 0, 180 * 16)
            painter.drawArc(QRectF(cx + 4, eye_y - 14, 12, 8), 0, 180 * 16)
        elif self.expression == "thinking":
            painter.drawLine(QPointF(cx - 15, eye_y - 8), QPointF(cx - 5, eye_y - 8))
            painter.drawLine(QPointF(cx + 5, eye_y - 10), QPointF(cx + 15, eye_y - 6))
        else:
            painter.drawArc(QRectF(cx - 15, eye_y - 10, 10, 6), 0, 180 * 16)
            painter.drawArc(QRectF(cx + 5, eye_y - 10, 10, 6), 0, 180 * 16)

    def _draw_eyes(self, painter: QPainter, cx: float, cy: float):
        eye_y = cy - 8
        if self.is_blinking:
            painter.setPen(QPen(QColor(50, 30, 20), 2))
            painter.drawLine(QPointF(cx - 13, eye_y), QPointF(cx - 5, eye_y))
            painter.drawLine(QPointF(cx + 5, eye_y), QPointF(cx + 13, eye_y))
        elif self.expression in ["surprised", "breakdown"]:
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(COLOR_WHITE))
            painter.drawEllipse(QRectF(cx - 14, eye_y - 5, 10, 10))
            painter.drawEllipse(QRectF(cx + 4, eye_y - 5, 10, 10))
            painter.setBrush(QBrush(QColor(50, 30, 20)))
            painter.drawEllipse(QRectF(cx - 11, eye_y - 2, 4, 4))
            painter.drawEllipse(QRectF(cx + 7, eye_y - 2, 4, 4))
        elif self.expression == "nervous":
            glance_x = math.sin(self.anim_time * 6.0) * 2.0
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(QColor(50, 30, 20)))
            painter.drawEllipse(QRectF(cx - 11 + glance_x, eye_y - 2, 5, 5))
            painter.drawEllipse(QRectF(cx + 6 + glance_x, eye_y - 2, 5, 5))
        else:
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(QColor(50, 30, 20)))
            painter.drawEllipse(QRectF(cx - 11, eye_y - 2, 5, 5))
            painter.drawEllipse(QRectF(cx + 6, eye_y - 2, 5, 5))

    def _draw_mouth(self, painter: QPainter, cx: float, cy: float):
        mouth_y = cy + 12
        if self.is_speaking:
            mouth_h = int((math.sin(self.anim_time * 15.0) + 1.0) * 3) + 3
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(QColor(90, 40, 35)))
            painter.drawEllipse(QRectF(cx - 6, mouth_y - 2, 12, mouth_h))
            painter.setPen(QPen(COLOR_WHITE, 1))
            painter.drawLine(QPointF(cx - 4, mouth_y), QPointF(cx + 4, mouth_y))
        elif self.expression == "breakdown":
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(QColor(120, 30, 25)))
            painter.drawEllipse(QRectF(cx - 8, mouth_y - 2, 16, 10))
            painter.setPen(QPen(COLOR_WHITE, 1))
            painter.drawLine(QPointF(cx - 5, mouth_y), QPointF(cx + 5, mouth_y))
        elif self.expression == "angry":
            painter.setPen(QPen(QColor(120, 45, 40), 2))
            painter.drawLine(QPointF(cx - 7, mouth_y + 2), QPointF(cx + 7, mouth_y + 2))
        elif self.expression == "satisfied":
            painter.setPen(QPen(QColor(130, 60, 50), 2))
            painter.drawArc(QRectF(cx - 7, mouth_y - 4, 14, 8), 180 * 16, 180 * 16)
        elif self.expression == "nervous":
            wobble = math.sin(self.anim_time * 10.0) * 1.5
            painter.setPen(QPen(QColor(130, 60, 50), 2))
            painter.drawLine(QPointF(cx - 6, mouth_y + wobble), QPointF(cx + 6, mouth_y - wobble))
        else:
            painter.setPen(QPen(QColor(130, 60, 50), 2))
            painter.drawLine(QPointF(cx - 5, mouth_y), QPointF(cx + 5, mouth_y))

    def _draw_overlays(self, painter: QPainter, cx: float, cy: float, w: float, h: float):
        # Spectacles for judge & doctor
        if self.character_type in ["judge", "doctor"]:
            painter.setPen(QPen(COLOR_GOLD, 1.5))
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(QRectF(cx - 13, cy - 12, 10, 10))
            painter.drawEllipse(QRectF(cx + 3, cy - 12, 10, 10))
            painter.drawLine(QPointF(cx - 3, cy - 7), QPointF(cx + 3, cy - 7))

        # Falling sweat drops for nervous / breakdown
        if self.expression in ["nervous", "breakdown"]:
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(QColor(120, 200, 255)))
            y1 = 15 + int((self.anim_time * 35.0) % (h - 30))
            y2 = 25 + int(((self.anim_time + 0.5) * 35.0) % (h - 30))
            painter.drawEllipse(QRectF(w - 18, y1, 5, 6))
            painter.drawEllipse(QRectF(12, y2, 5, 6))

        # Anger pop mark
        elif self.expression == "angry":
            painter.setPen(QPen(COLOR_ACCENT_RED, 2))
            px, py = w - 18, 14
            painter.drawLine(QPointF(px - 4, py - 4), QPointF(px + 4, py + 4))
            painter.drawLine(QPointF(px + 4, py - 4), QPointF(px - 4, py + 4))

