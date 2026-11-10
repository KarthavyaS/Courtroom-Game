"""Animated Dramatic Phoenix Wright 'OBJECTION!' Overlay for PySide6 LOGIC COURTROOM.
Features starburst speedlines, scaling impact with overshoot easing, and sound stingers.
"""

import math
from PySide6.QtCore import Qt, QTimer, QRectF, QPointF
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QFont
from PySide6.QtWidgets import QWidget

from app_qt.config import COLOR_GOLD, COLOR_GOLD_LIGHT, COLOR_WHITE, COLOR_ACCENT_RED
from app_qt.services.sound_service_qt import get_sound_service_qt


class ObjectionOverlay(QWidget):
    """Full-screen animated dramatic interjection banner."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        self.text = "OBJECTION!"
        self.speaker = "Defense Counsel"
        self.scale = 2.8
        self.timer_val = 0.0
        self.duration = 1.3
        self.active = False

        self.sound_service = get_sound_service_qt()

        self.anim_timer = QTimer(self)
        self.anim_timer.setInterval(20)
        self.anim_timer.timeout.connect(self._on_tick)

        self.hide()

    def trigger(self, text: str = "OBJECTION!", speaker: str = "Defense Counsel"):
        self.text = text
        self.speaker = speaker
        self.scale = 2.8
        self.timer_val = 0.0
        self.active = True

        if self.parent():
            self.setGeometry(0, 0, self.parent().width(), self.parent().height())
            self.raise_()

        self.sound_service.play("objection")
        self.show()
        self.anim_timer.start()

    def _on_tick(self):
        dt = 0.020
        self.timer_val += dt

        # Slam scale down to 1.0 within 0.25 seconds with overshoot
        if self.timer_val < 0.25:
            t = self.timer_val / 0.25
            # Ease out back: overshoot formula
            overshoot = 1.70158
            t_back = t - 1.0
            eased = t_back * t_back * ((overshoot + 1.0) * t_back + overshoot) + 1.0
            self.scale = 2.8 - eased * 1.8
        else:
            self.scale = 1.0

        if self.timer_val >= self.duration:
            self.active = False
            self.anim_timer.stop()
            self.hide()

        self.update()

    def paintEvent(self, event):
        if not self.active:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        cx = w / 2.0
        cy = h / 2.0 - 20.0

        # 1. Dark Letterbox Backdrop
        alpha = int(min(180, (1.0 - (self.timer_val / self.duration) ** 2) * 220))
        painter.fillRect(self.rect(), QColor(15, 8, 8, alpha))

        # 2. Dynamic Red Banner Stripe across screen
        stripe_h = 130.0
        stripe_rect = QRectF(0, cy - stripe_h / 2.0, w, stripe_h)
        painter.fillRect(stripe_rect, QColor(180, 25, 20, min(240, alpha + 30)))
        painter.setPen(QPen(COLOR_GOLD, 3))
        painter.drawLine(QPointF(0, stripe_rect.top()), QPointF(w, stripe_rect.top()))
        painter.drawLine(QPointF(0, stripe_rect.bottom()), QPointF(w, stripe_rect.bottom()))

        # 3. Rotating Starburst Speedlines
        painter.setPen(QPen(QColor(255, 240, 150, min(140, alpha)), 2))
        for i in range(16):
            ang = (i / 16.0) * math.pi * 2.0 + (self.timer_val * 4.0)
            lx = cx + math.cos(ang) * (w * 0.6)
            ly = cy + math.sin(ang) * (h * 0.4)
            painter.drawLine(QPointF(cx, cy), QPointF(lx, ly))

        # 4. Scaled Text Rendering
        f_size = int(36 * max(0.5, self.scale))
        font = QFont("Segoe UI", f_size, QFont.Bold)
        painter.setFont(font)

        main_text = f"★ {self.text} ★"
        # Shadow
        painter.setPen(QColor(40, 0, 0))
        painter.drawText(QRectF(4, cy - 36, w, 70), Qt.AlignCenter, main_text)
        # Foreground
        painter.setPen(COLOR_GOLD_LIGHT)
        painter.drawText(QRectF(0, cy - 40, w, 70), Qt.AlignCenter, main_text)

        # Speaker subtitle
        sub_font = QFont("Segoe UI", 12, QFont.Bold)
        painter.setFont(sub_font)
        painter.setPen(COLOR_WHITE)
        painter.drawText(QRectF(0, cy + 34, w, 24), Qt.AlignCenter, f"— {self.speaker.upper()} INTERJECTS —")

