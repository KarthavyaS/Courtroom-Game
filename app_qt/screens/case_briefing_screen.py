"""Formal Police Dossier and Case Briefing Screen for PySide6 LOGIC COURTROOM.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QTextBrowser
)
from services.game_state import GameState
from services.save_service import SaveService
from app_qt.config import (
    HEX_GOLD, HEX_GOLD_LIGHT, HEX_ACCENT_GREEN, HEX_LIGHT_PARCHMENT,
    HEX_MUTED_TEXT
)
from app_qt.services.sound_service_qt import get_sound_service_qt


class CaseBriefingScreenQt(QWidget):
    """Classified police dossier and legal briefing screen."""

    navigate = Signal(str)
    notify = Signal(str, str)
    enter_crime_scene = Signal()

    def __init__(self, game_state: GameState, save_service: SaveService, parent=None):
        super().__init__(parent)
        self.game_state = game_state
        self.save_service = save_service
        self.sound_service = get_sound_service_qt()

        self._build_ui()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(35, 20, 35, 20)
        main_layout.setSpacing(14)

        # Header Title
        lbl_title = QLabel("POLICE INCIDENT DOSSIER & FORMAL BRIEFING")
        lbl_title.setProperty("class", "title-gold")
        main_layout.addWidget(lbl_title)

        # Main Parchment Card
        card = QFrame()
        card.setProperty("class", "court-card-gold")
        card.setStyleSheet("background-color: #241610; border: 2px solid #ffd741; border-radius: 10px; padding: 18px;")
        c_layout = QVBoxLayout(card)
        c_layout.setSpacing(12)

        self.lbl_case_header = QLabel("CASE FILE #001: THE MIDNIGHT MURDER")
        self.lbl_case_header.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {HEX_GOLD}; border: none;")
        c_layout.addWidget(self.lbl_case_header)

        self.txt_dossier = QTextBrowser()
        self.txt_dossier.setStyleSheet("background-color: #19100c; border: 1px solid #5a351c; border-radius: 6px; padding: 14px; font-size: 13px; line-height: 1.6;")
        c_layout.addWidget(self.txt_dossier, 1)

        # Action Buttons
        btn_box = QHBoxLayout()
        btn_box.addStretch(1)

        self.btn_enter_scene = QPushButton("ENTER CRIME SCENE ➔")
        self.btn_enter_scene.setProperty("class", "btn-success")
        self.btn_enter_scene.setFixedHeight(44)
        self.btn_enter_scene.setStyleSheet("font-size: 13px; font-weight: bold; padding: 8px 28px;")
        self.btn_enter_scene.clicked.connect(self._on_enter_scene)
        btn_box.addWidget(self.btn_enter_scene)

        c_layout.addLayout(btn_box)
        main_layout.addWidget(card, 1)

    def on_enter_screen(self):
        case = self.game_state.current_case
        if not case:
            return

        self.game_state.progress.mark_briefing_read()
        self.save_service.save_active_game(self.game_state)

        self.lbl_case_header.setText(f"{case.id}: {case.title.upper()} — CLASSIFIED BRIEFING")

        html = f"""
        <h3 style='color: #ffd741; margin-top: 0;'>Location: {case.scene_name} ({case.scene_type.capitalize()})</h3>
        <p><b>Investigation Category:</b> {case.type.upper()}  |  <b>Judicial Honor Reward:</b> {case.reward} XP</p>
        <hr style='border: 1px solid #704222;'>
        <h4 style='color: #ffeb82;'>Incident Narrative:</h4>
        <p style='color: #f5ebd7; font-size: 13px; line-height: 1.6;'>{case.description}</p>
        <h4 style='color: #ffeb82;'>Initial Verified Forensic Facts:</h4>
        <ul style='color: #f5ebd7; font-size: 12px;'>
        """
        for fact in case.initial_facts:
            html += f"<li><b>{fact}</b></li>"
        html += f"""
        </ul>
        <h4 style='color: #ffeb82;'>Target Legal Objective:</h4>
        <p style='color: #2db955; font-size: 13px; font-weight: bold;'>
            Prove beyond reasonable doubt that the accused is guilty using valid propositional deduction rules.
        </p>
        <p style='color: #d8c8b8; font-size: 12px;'>
            Next Step: Enter the interactive 2D Crime Scene, sweep for latent artifacts with the forensic tool kit, and unlock vital premises into your Knowledge Base.
        </p>
        """
        self.txt_dossier.setHtml(html)

    def _on_enter_scene(self):
        self.sound_service.play("click")
        self.enter_crime_scene.emit()
        self.navigate.emit("crime_scene")

