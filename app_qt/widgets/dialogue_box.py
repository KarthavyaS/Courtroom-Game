"""Typewriter Dialogue Box Widget for PySide6 LOGIC COURTROOM.
Features typewriter character reveal, speaker ribbon header badges, and instant skip on click.
"""

from PySide6.QtCore import Qt, QTimer, Signal, QRectF
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QFont
from PySide6.QtWidgets import QWidget

from app_qt.config import (
    COLOR_BG_PANEL, COLOR_GOLD, COLOR_GOLD_LIGHT, COLOR_LIGHT_PARCHMENT,
    COLOR_WHITE, COLOR_ACCENT_RED, COLOR_ACCENT_BLUE, COLOR_ACCENT_GREEN
)
from app_qt.services.sound_service_qt import get_sound_service_qt


class DialogueBoxQt(QWidget):
    """Interactive typewriter dialogue panel for courtroom exchanges."""

    typewriter_completed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(140)
        self.setMinimumWidth(600)

        self.speaker: str = "Judge"
        self.full_text: str = ""
        self.displayed_text: str = ""
        self.char_index: float = 0.0
        self.typewriter_speed: float = 45.0  # chars per sec
        self.is_finished: bool = True

        self.speaker_color = COLOR_GOLD
        self.accent_color = COLOR_GOLD_LIGHT
        self.sound_service = get_sound_service_qt()

        self.timer = QTimer(self)
        self.timer.setInterval(22)  # ~45 FPS
        self.timer.timeout.connect(self._on_type_tick)

        self.setCursor(Qt.PointingHandCursor)

    def set_message(self, speaker: str, text: str, instant: bool = False):
        self.speaker = speaker or "Court"
        self.full_text = text or ""
        self.char_index = float(len(self.full_text)) if instant else 0.0
        self.displayed_text = self.full_text if instant else ""
        self.is_finished = instant

        # Dynamic color theme by speaker role
        sp_lower = self.speaker.lower()
        if "judge" in sp_lower or "magistrate" in sp_lower:
            self.speaker_color = COLOR_GOLD
            self.accent_color = COLOR_GOLD_LIGHT
        elif "counsel" in sp_lower or "player" in sp_lower or "lawyer" in sp_lower:
            self.speaker_color = COLOR_ACCENT_BLUE
            self.accent_color = QColor(135, 206, 250)
        elif "warning" in sp_lower or "bailiff" in sp_lower:
            self.speaker_color = COLOR_ACCENT_RED
            self.accent_color = QColor(255, 130, 130)
        else:
            self.speaker_color = COLOR_ACCENT_GREEN
            self.accent_color = QColor(160, 240, 160)

        if not instant:
            self.timer.start()
        else:
            self.timer.stop()

        self.update()

    def skip_typewriter(self):
        """Immediately displays full text."""
        if not self.is_finished:
            self.char_index = float(len(self.full_text))
            self.displayed_text = self.full_text
            self.is_finished = True
            self.timer.stop()
            self.update()
            self.typewriter_completed.emit()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if not self.is_finished:
                self.skip_typewriter()

    def _on_type_tick(self):
        if not self.is_finished:
            self.char_index += self.typewriter_speed * 0.022
            target_len = min(len(self.full_text), int(self.char_index))
            self.displayed_text = self.full_text[:target_len]

            # Play subtle typewriter click every 4th char
            if target_len > 0 and target_len % 4 == 0:
                self.sound_service.play("typewriter")

            if target_len >= len(self.full_text):
                self.is_finished = True
                self.timer.stop()
                self.typewriter_completed.emit()

            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()

        # 1. Main Background Box
        box_rect = QRectF(4, 18, w - 8, h - 22)
        painter.setPen(QPen(self.speaker_color, 2))
        painter.setBrush(QBrush(QColor(22, 14, 10)))
        painter.drawRoundedRect(box_rect, 10, 10)

        # Subtle inner fillet line
        painter.setPen(QPen(QColor(255, 255, 255, 25), 1))
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(box_rect.adjusted(4, 4, -4, -4), 8, 8)

        # 2. Speaker Ribbon Badge at Top Left
        ribbon_w = min(280.0, max(140.0, len(self.speaker) * 11.0 + 36.0))
        ribbon_rect = QRectF(24, 4, ribbon_w, 28)
        painter.setPen(QPen(self.speaker_color, 1.5))
        painter.setBrush(QBrush(QColor(42, 26, 18)))
        painter.drawRoundedRect(ribbon_rect, 6, 6)

        painter.setFont(QFont("Segoe UI", 11, QFont.Bold))
        painter.setPen(self.accent_color)
        painter.drawText(ribbon_rect, Qt.AlignCenter, self.speaker.upper())

        # 3. Message Text (Word-wrapped with Georgia typeface)
        text_rect = QRectF(24, 42, w - 48, h - 52)
        painter.setFont(QFont("Georgia", 13))
        painter.setPen(COLOR_LIGHT_PARCHMENT)
        painter.drawText(text_rect, Qt.AlignLeft | Qt.TextWordWrap, self.displayed_text)

        # 4. Blinking Advance Indicator when done typing
        if self.is_finished:
            painter.setFont(QFont("Segoe UI", 10, QFont.Bold))
            painter.setPen(COLOR_GOLD)
            painter.drawText(QRectF(w - 180, h - 24, 160, 20), Qt.AlignRight, "▼ [CLICK TO ADVANCE]")

