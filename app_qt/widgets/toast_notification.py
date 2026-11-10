"""Toast Notification Overlay Widget for PySide6 LOGIC COURTROOM.
"""

from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtWidgets import QFrame, QLabel, QHBoxLayout, QGraphicsOpacityEffect
from app_qt.config import (
    HEX_ACCENT_GREEN, HEX_ACCENT_RED, HEX_WOOD_BROWN, HEX_GOLD,
    HEX_GOLD_LIGHT, HEX_LIGHT_PARCHMENT
)

class ToastNotification(QFrame):
    """Floating banner displayed at top center of window."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(44)
        self.setMinimumWidth(320)
        self.setMaximumWidth(700)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(18, 6, 18, 6)
        layout.setSpacing(10)

        self.lbl_icon = QLabel("ℹ")
        self.lbl_icon.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(self.lbl_icon)

        self.lbl_text = QLabel("")
        self.lbl_text.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {HEX_LIGHT_PARCHMENT};")
        self.lbl_text.setWordWrap(False)
        layout.addWidget(self.lbl_text)

        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(0.0)

        self.dismiss_timer = QTimer(self)
        self.dismiss_timer.setSingleShot(True)
        self.dismiss_timer.timeout.connect(self._fade_out)

        self.fade_anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_anim.setDuration(240)
        self.fade_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)

        self.hide()

    def show_message(self, message: str, category: str = "INFO", duration_ms: int = 3200):
        category = (category or "INFO").upper()

        if category == "SUCCESS":
            bg_col = "#1f5f33"
            bdr_col = HEX_ACCENT_GREEN
            icon = "✓"
            icon_col = HEX_ACCENT_GREEN
        elif category == "ERROR":
            bg_col = "#631d1a"
            bdr_col = HEX_ACCENT_RED
            icon = "✗"
            icon_col = HEX_ACCENT_RED
        elif category == "WARNING":
            bg_col = "#5a3a12"
            bdr_col = HEX_GOLD
            icon = "⚠"
            icon_col = HEX_GOLD_LIGHT
        else:
            bg_col = "#382318"
            bdr_col = HEX_GOLD
            icon = "ℹ"
            icon_col = HEX_GOLD_LIGHT

        self.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_col};
                border: 2px solid {bdr_col};
                border-radius: 8px;
            }}
        """)
        self.lbl_icon.setText(icon)
        self.lbl_icon.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {icon_col};")
        self.lbl_text.setText(message)
        self.adjustSize()

        if self.parent():
            parent_w = self.parent().width()
            my_w = self.width()
            self.move((parent_w - my_w) // 2, 54)

        self.show()
        self.raise_()

        self.fade_anim.stop()
        self.fade_anim.setStartValue(self.opacity_effect.opacity())
        self.fade_anim.setEndValue(1.0)
        self.fade_anim.start()

        self.dismiss_timer.stop()
        self.dismiss_timer.start(duration_ms)

    def _fade_out(self):
        self.fade_anim.stop()
        self.fade_anim.setStartValue(self.opacity_effect.opacity())
        self.fade_anim.setEndValue(0.0)
        self.fade_anim.finished.connect(self._on_fade_out_finished)
        self.fade_anim.start()

    def _on_fade_out_finished(self):
        try:
            self.fade_anim.finished.disconnect(self._on_fade_out_finished)
        except Exception:
            pass
        if self.opacity_effect.opacity() == 0.0:
            self.hide()

