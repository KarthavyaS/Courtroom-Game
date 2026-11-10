"""Unified Top Stage Navigation Bar for PySide6 LOGIC COURTROOM.
"""

from typing import Optional
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QPushButton, QLabel, QProgressBar, QSlider
)
from app_qt.config import (
    HEX_GOLD, HEX_GOLD_LIGHT, HEX_WOOD_BROWN, HEX_BG_PANEL, HEX_BORDER,
    HEX_ACCENT_GREEN
)
from app_qt.services.sound_service_qt import get_sound_service_qt


class NavigationBarQt(QFrame):
    """Top horizontal toolbar providing stage-to-stage navigation and quick controls."""

    stage_selected = Signal(str)
    minimize_requested = Signal()

    STAGES = [
        ("briefing", "BRIEFING"),
        ("crime_scene", "SCENE"),
        ("suspects", "SUSPECTS"),
        ("evidence", "EVIDENCE"),
        ("case_board", "BOARD"),
        ("notebook", "NOTEBOOK"),
        ("arguments", "ARGUMENTS"),
        ("courtroom", "⚖ COURT")
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(46)
        self.setProperty("class", "header-strip")
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #2b180f;
                border-bottom: 2px solid {HEX_GOLD};
            }}
        """)

        self.active_stage = "briefing"
        self.buttons: dict[str, QPushButton] = {}
        self.sound_service = get_sound_service_qt()

        self._build_ui()

    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 4, 12, 4)
        layout.setSpacing(6)

        # 1. Main Menu & Hub / Dashboard Buttons
        btn_menu = QPushButton("⌂ MENU")
        btn_menu.setProperty("class", "btn-nav")
        btn_menu.setStyleSheet(f"""
            QPushButton {{
                background-color: #2b1f14;
                border: 1px solid #704222;
                font-size: 11px;
                font-weight: bold;
                padding: 4px 10px;
                min-height: 24px;
            }}
            QPushButton:hover {{
                background-color: #422f1f;
                border: 1px solid {HEX_GOLD_LIGHT};
                color: #ffffff;
            }}
        """)
        btn_menu.clicked.connect(lambda: self._on_button_clicked("welcome"))
        layout.addWidget(btn_menu)

        btn_hub = QPushButton("🏢 HUB")
        btn_hub.setProperty("class", "btn-nav")
        btn_hub.setStyleSheet(f"""
            QPushButton {{
                background-color: #42291e;
                border: 1px solid {HEX_GOLD_LIGHT};
                font-size: 11px;
                font-weight: bold;
                padding: 4px 12px;
                min-height: 24px;
            }}
            QPushButton:hover {{
                background-color: #5c3829;
            }}
        """)
        btn_hub.clicked.connect(lambda: self._on_button_clicked("dashboard"))
        layout.addWidget(btn_hub)

        # 2. Stage Tabs
        for stage_id, label in self.STAGES:
            btn = QPushButton(label)
            btn.setProperty("class", "btn-nav")
            btn.setFixedHeight(28)
            btn.clicked.connect(lambda checked=False, s=stage_id: self._on_button_clicked(s))
            self.buttons[stage_id] = btn
            layout.addWidget(btn)

        layout.addStretch(1)

        # 3. Investigation Progress Bar
        self.lbl_progress = QLabel("Progress: 0%")
        self.lbl_progress.setStyleSheet(f"font-size: 11px; font-weight: bold; color: {HEX_GOLD};")
        layout.addWidget(self.lbl_progress)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedSize(110, 14)
        layout.addWidget(self.progress_bar)

        # 4. Audio Control
        self.btn_audio = QPushButton("🔊")
        self.btn_audio.setToolTip("Toggle Audio Mute")
        self.btn_audio.setFixedSize(28, 28)
        self.btn_audio.setStyleSheet("background-color: #382318; border: 1px solid #704222; font-size: 13px; padding: 0px;")
        self.btn_audio.clicked.connect(self._toggle_audio)
        layout.addWidget(self.btn_audio)

        # 5. Window Minimize Button
        btn_min = QPushButton("—")
        btn_min.setToolTip("Minimize Window (Ctrl+M)")
        btn_min.setFixedSize(28, 28)
        btn_min.setStyleSheet(f"""
            QPushButton {{
                background-color: #422419;
                border: 1px solid {HEX_GOLD};
                font-size: 13px;
                font-weight: bold;
                padding: 0px;
            }}
            QPushButton:hover {{
                background-color: #633626;
            }}
        """)
        btn_min.clicked.connect(self.minimize_requested.emit)
        layout.addWidget(btn_min)

        self.set_active_stage("briefing")

    def _on_button_clicked(self, stage_id: str):
        self.sound_service.play("click")
        self.set_active_stage(stage_id)
        self.stage_selected.emit(stage_id)

    def set_active_stage(self, stage_id: str):
        self.active_stage = stage_id
        for sid, btn in self.buttons.items():
            if sid == stage_id:
                btn.setStyleSheet(f"""
                    background-color: #965f23;
                    border: 1px solid {HEX_GOLD};
                    color: #ffffff;
                    font-weight: bold;
                    border-radius: 5px;
                """)
            else:
                btn.setStyleSheet(f"""
                    background-color: #291a13;
                    border: 1px solid #633c22;
                    color: #d8c8b8;
                    border-radius: 5px;
                """)

    def update_progress(self, percentage: int):
        pct = max(0, min(100, int(percentage)))
        self.progress_bar.setValue(pct)
        self.lbl_progress.setText(f"Progress: {pct}%")

    def _toggle_audio(self):
        new_muted = not self.sound_service.is_muted
        self.sound_service.set_muted(new_muted)
        self.btn_audio.setText("🔇" if new_muted else "🔊")

