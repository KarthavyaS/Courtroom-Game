"""Welcome and Player Onboarding Screen for PySide6 LOGIC COURTROOM.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QFrame
)
from services.game_state import GameState
from services.save_service import SaveService
from app_qt.config import (
    HEX_GOLD, HEX_GOLD_LIGHT, HEX_ACCENT_GREEN, HEX_LIGHT_PARCHMENT,
    HEX_MUTED_TEXT, GAME_TITLE, TAGLINE
)
from app_qt.services.sound_service_qt import get_sound_service_qt


class WelcomeScreenQt(QWidget):
    """Initial title, player naming onboarding, and game launch screen."""

    navigate = Signal(str)
    notify = Signal(str, str)
    start_game = Signal()
    continue_game = Signal()

    def __init__(self, game_state: GameState, save_service: SaveService, parent=None):
        super().__init__(parent)
        self.game_state = game_state
        self.save_service = save_service
        self.sound_service = get_sound_service_qt()

        self._build_ui()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 30, 40, 30)
        main_layout.setAlignment(Qt.AlignCenter)

        # Centered Golden Card Frame
        card = QFrame()
        card.setProperty("class", "court-card-gold")
        card.setFixedSize(680, 520)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(40, 30, 40, 30)
        card_layout.setSpacing(16)
        card_layout.setAlignment(Qt.AlignCenter)

        # Scales / Gavel Emblem
        lbl_icon = QLabel("⚖️")
        lbl_icon.setStyleSheet("font-size: 52px;")
        lbl_icon.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(lbl_icon)

        # Title & Tagline
        lbl_title = QLabel(GAME_TITLE)
        lbl_title.setStyleSheet(f"font-size: 32px; font-weight: bold; color: {HEX_GOLD}; letter-spacing: 2px;")
        lbl_title.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(lbl_title)

        lbl_tagline = QLabel(f"« {TAGLINE} »")
        lbl_tagline.setStyleSheet(f"font-size: 14px; font-style: italic; color: {HEX_GOLD_LIGHT};")
        lbl_tagline.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(lbl_tagline)

        # Lore / Synopsis Box
        lbl_lore = QLabel(
            "Step into the Victorian Old Bailey as Lead Legal Advocate.\n"
            "Investigate crime scenes, scrutinize suspect alibis, and construct rigorous deductive arguments.\n"
            "Every verdict is adjudicated through deterministic Symbolic Artificial Intelligence."
        )
        lbl_lore.setStyleSheet(f"font-size: 12px; color: {HEX_LIGHT_PARCHMENT}; line-height: 1.6; text-align: center;")
        lbl_lore.setWordWrap(True)
        lbl_lore.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(lbl_lore)

        # Onboarding Name Input Frame
        self.onboarding_box = QFrame()
        self.onboarding_box.setStyleSheet("background-color: #1a100b; border: 1px solid #704222; border-radius: 8px; padding: 10px;")
        ob_layout = QVBoxLayout(self.onboarding_box)
        ob_layout.setSpacing(8)

        lbl_prompt = QLabel("ENTER ADVOCATE IDENTITY:")
        lbl_prompt.setStyleSheet(f"font-size: 11px; font-weight: bold; color: {HEX_GOLD};")
        lbl_prompt.setAlignment(Qt.AlignCenter)
        ob_layout.addWidget(lbl_prompt)

        self.tb_name = QLineEdit(self.game_state.profile.name)
        self.tb_name.setPlaceholderText("Enter your lawyer name...")
        self.tb_name.setAlignment(Qt.AlignCenter)
        self.tb_name.setFixedHeight(36)
        ob_layout.addWidget(self.tb_name)
        card_layout.addWidget(self.onboarding_box)

        # Launch Buttons
        btn_box = QHBoxLayout()
        btn_box.setSpacing(12)

        self.btn_start = QPushButton("INVESTIGATION HUB ➔")
        self.btn_start.setProperty("class", "btn-success")
        self.btn_start.setFixedHeight(44)
        self.btn_start.clicked.connect(self._handle_start)
        btn_box.addWidget(self.btn_start)

        self.btn_courtroom = QPushButton("ENTER COURTROOM ⚖")
        self.btn_courtroom.setProperty("class", "btn-gold")
        self.btn_courtroom.setFixedHeight(44)
        self.btn_courtroom.clicked.connect(self._handle_enter_courtroom)
        btn_box.addWidget(self.btn_courtroom)

        self.btn_continue = QPushButton("CONTINUE CASE ➔")
        self.btn_continue.setProperty("class", "btn-gold")
        self.btn_continue.setFixedHeight(44)
        self.btn_continue.clicked.connect(self._handle_continue)
        btn_box.addWidget(self.btn_continue)

        card_layout.addLayout(btn_box)
        main_layout.addWidget(card, 0, Qt.AlignCenter)

    def on_enter_screen(self):
        """Called whenever the screen becomes visible."""
        has_save = self.save_service.has_active_save()
        self.btn_continue.setVisible(has_save)
        self.tb_name.setText(self.game_state.profile.name)

    def _handle_start(self):
        name = self.tb_name.text().strip()
        if name:
            self.game_state.profile.name = name
            self.game_state.player_name = name
            self.save_service.save_profile(self.game_state.profile)

        self.sound_service.play("gavel")
        self.start_game.emit()
        self.navigate.emit("dashboard")

    def _handle_enter_courtroom(self):
        name = self.tb_name.text().strip()
        if name:
            self.game_state.profile.name = name
            self.game_state.player_name = name
            self.save_service.save_profile(self.game_state.profile)

        self.sound_service.play("gavel")
        self.navigate.emit("courtroom")

    def _handle_continue(self):
        self.sound_service.play("gavel")
        self.continue_game.emit()
        if self.game_state.current_case:
            self.navigate.emit("briefing")
        else:
            self.navigate.emit("dashboard")

