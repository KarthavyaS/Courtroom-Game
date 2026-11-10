"""Interactive Academy Walkthrough Screen for PySide6 LOGIC COURTROOM.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QTextBrowser
)
from services.game_state import GameState
from services.save_service import SaveService
from services.tutorial_service import TutorialService
from app_qt.config import (
    HEX_GOLD, HEX_GOLD_LIGHT, HEX_ACCENT_GREEN, HEX_LIGHT_PARCHMENT,
    HEX_MUTED_TEXT
)
from app_qt.services.sound_service_qt import get_sound_service_qt


class TutorialScreenQt(QWidget):
    """7-step interactive Academy of Law walkthrough screen."""

    navigate = Signal(str)
    notify = Signal(str, str)
    tutorial_finished = Signal()

    def __init__(self, game_state: GameState, save_service: SaveService, parent=None):
        super().__init__(parent)
        self.game_state = game_state
        self.save_service = save_service
        self.tutorial_service = TutorialService()
        self.sound_service = get_sound_service_qt()

        self._build_ui()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 24, 40, 24)
        main_layout.setSpacing(16)

        # Header bar
        header_box = QHBoxLayout()
        lbl_header = QLabel("ACADEMY OF LAW — INTERACTIVE TUTORIAL")
        lbl_header.setProperty("class", "title-gold")
        header_box.addWidget(lbl_header)

        self.lbl_stage_counter = QLabel("STAGE 1 OF 7")
        self.lbl_stage_counter.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {HEX_GOLD_LIGHT};")
        header_box.addWidget(self.lbl_stage_counter, 0, Qt.AlignRight)
        main_layout.addLayout(header_box)

        # Step Progress Pills
        self.pills_layout = QHBoxLayout()
        self.pills_layout.setSpacing(6)
        self.pills = []
        for _ in range(self.tutorial_service.total_steps):
            pill = QFrame()
            pill.setFixedHeight(8)
            pill.setStyleSheet("background-color: #382419; border-radius: 4px;")
            self.pills_layout.addWidget(pill)
            self.pills.append(pill)
        main_layout.addLayout(self.pills_layout)

        # Main Tutorial Card
        card = QFrame()
        card.setProperty("class", "court-card-gold")
        c_layout = QVBoxLayout(card)
        c_layout.setContentsMargins(32, 24, 32, 24)
        c_layout.setSpacing(14)

        self.lbl_step_title = QLabel("")
        self.lbl_step_title.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {HEX_GOLD};")
        c_layout.addWidget(self.lbl_step_title)

        self.lbl_step_subtitle = QLabel("")
        self.lbl_step_subtitle.setStyleSheet(f"font-size: 13px; font-style: italic; color: {HEX_GOLD_LIGHT};")
        c_layout.addWidget(self.lbl_step_subtitle)

        self.txt_description = QTextBrowser()
        self.txt_description.setStyleSheet("background-color: #1a100b; border: 1px solid #704222; border-radius: 8px; padding: 14px; font-size: 13px; line-height: 1.6;")
        c_layout.addWidget(self.txt_description, 1)

        # Key Takeaway Box
        self.takeaway_box = QFrame()
        self.takeaway_box.setStyleSheet("background-color: #2b1f14; border: 1px solid #ffd741; border-radius: 6px; padding: 10px;")
        t_layout = QHBoxLayout(self.takeaway_box)
        self.lbl_takeaway = QLabel("")
        self.lbl_takeaway.setStyleSheet(f"font-size: 12px; font-weight: bold; color: {HEX_GOLD_LIGHT};")
        t_layout.addWidget(self.lbl_takeaway)
        c_layout.addWidget(self.takeaway_box)

        main_layout.addWidget(card, 1)

        # Navigation Buttons Bar
        btn_box = QHBoxLayout()
        btn_box.setSpacing(14)

        self.btn_prev = QPushButton("← PREVIOUS")
        self.btn_prev.setStyleSheet("background-color: #423026; padding: 10px 20px;")
        self.btn_prev.clicked.connect(self._handle_prev)
        btn_box.addWidget(self.btn_prev)

        btn_box.addStretch(1)

        self.btn_skip = QPushButton("SKIP TUTORIAL")
        self.btn_skip.setStyleSheet("background-color: #592924; border: 1px solid #eb3732; padding: 10px 18px;")
        self.btn_skip.clicked.connect(self._handle_finish)
        btn_box.addWidget(self.btn_skip)

        self.btn_next = QPushButton("NEXT STEP ➔")
        self.btn_next.setProperty("class", "btn-success")
        self.btn_next.setStyleSheet("padding: 10px 24px;")
        self.btn_next.clicked.connect(self._handle_next)
        btn_box.addWidget(self.btn_next)

        self.btn_finish = QPushButton("START PLAYING ➔")
        self.btn_finish.setProperty("class", "btn-success")
        self.btn_finish.setStyleSheet("padding: 10px 24px;")
        self.btn_finish.clicked.connect(self._handle_finish)
        btn_box.addWidget(self.btn_finish)

        main_layout.addLayout(btn_box)

    def on_enter_screen(self):
        self.tutorial_service.current_step_index = 0
        self._update_step_display()

    def _update_step_display(self):
        step = self.tutorial_service.current_step_data
        idx = self.tutorial_service.current_step_index
        tot = self.tutorial_service.total_steps

        self.lbl_stage_counter.setText(f"STAGE {idx + 1} OF {tot}")
        self.lbl_step_title.setText(step.get("title", ""))
        self.lbl_step_subtitle.setText(step.get("subtitle", ""))
        self.txt_description.setText(step.get("description", ""))
        self.lbl_takeaway.setText(step.get("key_takeaway", ""))

        # Update Pills
        for i, pill in enumerate(self.pills):
            if i == idx:
                pill.setStyleSheet(f"background-color: {HEX_GOLD}; border-radius: 4px;")
            elif i < idx:
                pill.setStyleSheet(f"background-color: {HEX_ACCENT_GREEN}; border-radius: 4px;")
            else:
                pill.setStyleSheet("background-color: #382419; border-radius: 4px;")

        self.btn_prev.setEnabled(idx > 0)
        is_last = (idx >= tot - 1)
        self.btn_next.setVisible(not is_last)
        self.btn_finish.setVisible(is_last)

    def _handle_next(self):
        self.sound_service.play("click")
        self.tutorial_service.next_step()
        self._update_step_display()

    def _handle_prev(self):
        self.sound_service.play("click")
        self.tutorial_service.prev_step()
        self._update_step_display()

    def _handle_finish(self):
        self.sound_service.play("gavel")
        self.game_state.profile.tutorial_completed = True
        self.save_service.save_profile(self.game_state.profile)
        self.tutorial_finished.emit()
        self.navigate.emit("dashboard")

