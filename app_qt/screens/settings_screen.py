"""Settings and Accessibility Screen for PySide6 LOGIC COURTROOM.
Allows configuring Sound FX, Courtroom Ambient Music, Volume,
replaying the Academy Interactive Tutorial, and resetting all player progress.
"""

from typing import Optional
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QSlider, QSizePolicy
)

from services.game_state import GameState
from services.save_service import SaveService
from app_qt.config import (
    COLOR_BG_CARD, COLOR_BG_PANEL, COLOR_BORDER, COLOR_GOLD, COLOR_GOLD_LIGHT,
    COLOR_WHITE, COLOR_TEXT_MUTED, COLOR_TEXT_PARCHMENT, COLOR_ACCENT_GREEN,
    COLOR_ACCENT_RED, COLOR_ACCENT_BLUE, get_qt_font
)
from app_qt.services.sound_service_qt import get_sound_service_qt
from app_qt.dialogs.confirmation_dialog import ConfirmationDialogQt


class SettingsScreenQt(QWidget):
    """Settings and audio configuration screen."""

    navigate = Signal(str)
    notify = Signal(str, str)

    def __init__(self, game_state: GameState, save_service: Optional[SaveService] = None, parent=None):
        super().__init__(parent)
        self.game_state = game_state
        self.save_service = save_service or SaveService()
        self.sound_service = get_sound_service_qt()

        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 24, 40, 24)
        main_layout.setSpacing(16)

        # 1. Header with back button
        header_layout = QHBoxLayout()
        btn_back = QPushButton("← DASHBOARD")
        btn_back.setFont(get_qt_font(10, bold=True))
        btn_back.setStyleSheet("padding: 7px 16px; background-color: #2b1f14; color: #c9a050; border: 1px solid #5a381e; border-radius: 4px;")
        btn_back.clicked.connect(lambda: self.navigate.emit("dashboard"))
        header_layout.addWidget(btn_back)

        title_lbl = QLabel("CHAMBER SETTINGS & PREFERENCES")
        title_lbl.setFont(get_qt_font(16, bold=True))
        title_lbl.setStyleSheet(f"color: {COLOR_GOLD.name()}; margin-left: 12px;")
        header_layout.addWidget(title_lbl)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)

        # 2. Settings Card Container
        center_frame = QFrame()
        center_frame.setMaximumWidth(680)
        center_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLOR_BG_CARD.name()};
                border: 1px solid {COLOR_BORDER.name()};
                border-radius: 8px;
            }}
        """)
        c_layout = QVBoxLayout(center_frame)
        c_layout.setContentsMargins(30, 26, 30, 26)
        c_layout.setSpacing(18)

        # SFX Row
        self.btn_sfx = QPushButton()
        self.btn_sfx.setFont(get_qt_font(11, bold=True))
        self.btn_sfx.setFixedHeight(46)
        self.btn_sfx.clicked.connect(self._toggle_sfx)
        c_layout.addWidget(self.btn_sfx)

        # Music Row
        self.btn_music = QPushButton()
        self.btn_music.setFont(get_qt_font(11, bold=True))
        self.btn_music.setFixedHeight(46)
        self.btn_music.clicked.connect(self._toggle_music)
        c_layout.addWidget(self.btn_music)

        # Volume Slider Row
        vol_frame = QFrame()
        vol_frame.setStyleSheet("background-color: #1a120c; border: 1px solid #3d2b1f; border-radius: 6px; padding: 10px;")
        vol_layout = QVBoxLayout(vol_frame)
        vol_layout.setSpacing(8)

        vol_header = QHBoxLayout()
        vol_title = QLabel("MASTER AUDIO VOLUME:")
        vol_title.setFont(get_qt_font(10, bold=True))
        vol_title.setStyleSheet(f"color: {COLOR_GOLD.name()};")
        vol_header.addWidget(vol_title)

        self.lbl_volume = QLabel("100%")
        self.lbl_volume.setFont(get_qt_font(10, bold=True))
        self.lbl_volume.setStyleSheet("color: #ffffff;")
        vol_header.addWidget(self.lbl_volume, alignment=Qt.AlignRight)
        vol_layout.addLayout(vol_header)

        self.slider_volume = QSlider(Qt.Horizontal)
        self.slider_volume.setRange(0, 100)
        self.slider_volume.setValue(int(self.game_state.profile.volume * 100))
        self.slider_volume.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                background: #120d09;
                height: 8px;
                border-radius: 4px;
            }}
            QSlider::sub-page:horizontal {{
                background: {COLOR_GOLD.name()};
                border-radius: 4px;
            }}
            QSlider::handle:horizontal {{
                background: #fff;
                border: 2px solid {COLOR_GOLD.name()};
                width: 18px;
                margin-top: -5px;
                margin-bottom: -5px;
                border-radius: 9px;
            }}
        """)
        self.slider_volume.valueChanged.connect(self._on_volume_changed)
        vol_layout.addWidget(self.slider_volume)
        c_layout.addWidget(vol_frame)

        # Tutorial Replay Button
        btn_tutorial = QPushButton("🎓 REPLAY ACADEMY TUTORIAL")
        btn_tutorial.setFont(get_qt_font(11, bold=True))
        btn_tutorial.setFixedHeight(46)
        btn_tutorial.setStyleSheet("background-color: #1e3a5f; color: #ffffff; border: 1px solid #3a75b4; border-radius: 6px;")
        btn_tutorial.clicked.connect(lambda: self.navigate.emit("tutorial"))
        c_layout.addWidget(btn_tutorial)

        # Danger Zone: Reset Progress
        btn_reset = QPushButton("⚠ RESET ALL SAVED PROGRESS")
        btn_reset.setFont(get_qt_font(11, bold=True))
        btn_reset.setFixedHeight(46)
        btn_reset.setStyleSheet(f"background-color: #551a1a; color: #ff9999; border: 1px solid {COLOR_ACCENT_RED.name()}; border-radius: 6px;")
        btn_reset.clicked.connect(self._prompt_reset)
        c_layout.addWidget(btn_reset)

        main_layout.addWidget(center_frame, alignment=Qt.AlignCenter)
        main_layout.addStretch()

        self._refresh_control_states()

    def _refresh_control_states(self):
        sfx_on = self.game_state.profile.sound_enabled
        self.btn_sfx.setText("SOUND FX: ENABLED [ON]" if sfx_on else "SOUND FX: MUTED [OFF]")
        self.btn_sfx.setStyleSheet(f"background-color: {'#183318' if sfx_on else '#3a1e1e'}; color: {'#a0e0a0' if sfx_on else '#e0a0a0'}; border: 1px solid {'#3d8c3d' if sfx_on else '#883333'}; border-radius: 6px;")

        mus_on = self.game_state.profile.music_enabled
        self.btn_music.setText("COURTROOM MUSIC: PLAYING [ON]" if mus_on else "COURTROOM MUSIC: MUTED [OFF]")
        self.btn_music.setStyleSheet(f"background-color: {'#183318' if mus_on else '#3a1e1e'}; color: {'#a0e0a0' if mus_on else '#e0a0a0'}; border: 1px solid {'#3d8c3d' if mus_on else '#883333'}; border-radius: 6px;")

        vol = int(self.game_state.profile.volume * 100)
        self.lbl_volume.setText(f"{vol}%")
        self.slider_volume.setValue(vol)

    def _toggle_sfx(self):
        self.game_state.profile.sound_enabled = not self.game_state.profile.sound_enabled
        self.sound_service.set_sound_enabled(self.game_state.profile.sound_enabled)
        self.save_service.save_profile(self.game_state.profile)
        self.sound_service.play("click")
        self._refresh_control_states()

    def _toggle_music(self):
        self.game_state.profile.music_enabled = not self.game_state.profile.music_enabled
        self.sound_service.set_music_enabled(self.game_state.profile.music_enabled)
        self.save_service.save_profile(self.game_state.profile)
        self.sound_service.play("click")
        self._refresh_control_states()

    def _on_volume_changed(self, value: int):
        vol = value / 100.0
        self.game_state.profile.volume = vol
        self.lbl_volume.setText(f"{value}%")
        self.sound_service.set_volume(vol)
        self.save_service.save_profile(self.game_state.profile)

    def _prompt_reset(self):
        self.sound_service.play("click")
        dialog = ConfirmationDialogQt(
            title="RESET ALL PROGRESS?",
            message="This will permanently erase all career statistics, high scores, and active investigation saves.",
            confirm_text="ERASE DATA",
            cancel_text="CANCEL",
            parent=self
        )
        if dialog.exec():
            self.save_service.reset_all_progress()
            self.game_state.profile = self.save_service.load_profile()
            self.sound_service.play("gavel")
            self.notify.emit("WARNING", "All progress has been reset to defaults.")
            self._refresh_control_states()

    def on_enter_screen(self):
        self._refresh_control_states()

