"""Suspect Dossier, Interrogation & Cross-Examination Screen for PySide6 LOGIC COURTROOM.
"""

from typing import Optional, Dict
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget,
    QListWidgetItem, QFrame, QTabWidget, QTextBrowser, QProgressBar
)
from models.suspect import Suspect
from services.game_state import GameState
from services.save_service import SaveService
from app_qt.config import (
    HEX_GOLD, HEX_GOLD_LIGHT, HEX_ACCENT_GREEN, HEX_ACCENT_RED,
    HEX_ACCENT_BLUE, HEX_LIGHT_PARCHMENT, HEX_MUTED_TEXT
)
from app_qt.widgets.character_avatar import CharacterAvatarQt
from app_qt.services.sound_service_qt import get_sound_service_qt

PREDEFINED_QUESTIONS = [
    ("Q1", "Where were you at the time of the incident?"),
    ("Q2", "What was your relationship with the victim?"),
    ("Q3", "Did you see anyone near the crime scene?"),
    ("Q4", "Why were you present at the location?"),
    ("Q5", "Can you explain the inconsistencies in your story?")
]


class SuspectDetailsScreenQt(QWidget):
    """Suspect interrogation and profile cross-examination screen."""

    navigate = Signal(str)
    notify = Signal(str, str)
    proceed_to_board = Signal()
    notification_triggered = Signal(str, str)

    def __init__(self, game_state: GameState, save_service: SaveService, parent=None):
        super().__init__(parent)
        self.game_state = game_state
        self.save_service = save_service
        self.sound_service = get_sound_service_qt()

        self.selected_suspect: Optional[Suspect] = None
        self.suspect_stress: Dict[str, float] = {}

        self._build_ui()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 14, 25, 14)
        main_layout.setSpacing(12)

        # Header Bar
        top_bar = QHBoxLayout()
        lbl_title = QLabel("SUSPECT DOSSIERS & INTERROGATION CHAMBER")
        lbl_title.setProperty("class", "title-gold")
        top_bar.addWidget(lbl_title)
        top_bar.addStretch(1)

        btn_proceed = QPushButton("CASE BOARD ➔")
        btn_proceed.setProperty("class", "btn-gold")
        btn_proceed.setFixedHeight(34)
        btn_proceed.clicked.connect(self._on_proceed)
        top_bar.addWidget(btn_proceed)
        main_layout.addLayout(top_bar)

        # Main Content Layout: Left List, Right Dossier Tabs + Q&A
        content_box = QHBoxLayout()
        content_box.setSpacing(14)

        # 1. Left Suspect Selector
        left_frame = QFrame()
        left_frame.setProperty("class", "court-panel")
        left_frame.setFixedWidth(290)
        l_layout = QVBoxLayout(left_frame)
        l_layout.setContentsMargins(8, 8, 8, 8)

        lbl_s_list = QLabel("INDICTED PERSONS OF INTEREST:")
        lbl_s_list.setStyleSheet(f"font-size: 11px; font-weight: bold; color: {HEX_GOLD};")
        l_layout.addWidget(lbl_s_list)

        self.suspect_list = QListWidget()
        self.suspect_list.currentRowChanged.connect(self._on_suspect_row_changed)
        l_layout.addWidget(self.suspect_list, 1)
        content_box.addWidget(left_frame)

        # 2. Right Dossier Frame
        right_frame = QFrame()
        right_frame.setProperty("class", "court-card-gold")
        r_layout = QVBoxLayout(right_frame)
        r_layout.setContentsMargins(16, 12, 16, 12)
        r_layout.setSpacing(10)

        # Suspect Header Strip: Avatar + Name + Stress Bar
        header_strip = QHBoxLayout()
        header_strip.setSpacing(14)

        self.avatar_widget = CharacterAvatarQt()
        self.avatar_widget.setFixedSize(90, 95)
        header_strip.addWidget(self.avatar_widget)

        s_meta = QVBoxLayout()
        s_meta.setSpacing(4)
        self.lbl_suspect_name = QLabel("SUSPECT NAME")
        self.lbl_suspect_name.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {HEX_GOLD};")
        s_meta.addWidget(self.lbl_suspect_name)

        self.lbl_suspect_role = QLabel("Occupation: Unknown  |  Relationship: None")
        self.lbl_suspect_role.setStyleSheet(f"font-size: 12px; color: {HEX_LIGHT_PARCHMENT};")
        s_meta.addWidget(self.lbl_suspect_role)

        # Stress / Agitation Gauge
        stress_box = QHBoxLayout()
        lbl_stress = QLabel("Agitation Level:")
        lbl_stress.setStyleSheet("font-size: 11px; font-weight: bold; color: #ffeb82;")
        stress_box.addWidget(lbl_stress)

        self.stress_bar = QProgressBar()
        self.stress_bar.setRange(0, 100)
        self.stress_bar.setValue(20)
        self.stress_bar.setFixedHeight(12)
        stress_box.addWidget(self.stress_bar, 1)
        s_meta.addLayout(stress_box)

        header_strip.addLayout(s_meta, 1)
        r_layout.addLayout(header_strip)

        # 6-Tab Dossier View
        self.dossier_tabs = QTabWidget()
        self.tab_profile = QTextBrowser()
        self.tab_motive = QTextBrowser()
        self.tab_alibi = QTextBrowser()
        self.tab_testimony = QTextBrowser()
        self.tab_contradictions = QTextBrowser()
        self.tab_interview = QWidget()

        self.dossier_tabs.addTab(self.tab_profile, "PROFILE")
        self.dossier_tabs.addTab(self.tab_motive, "MOTIVE")
        self.dossier_tabs.addTab(self.tab_alibi, "ALIBI")
        self.dossier_tabs.addTab(self.tab_testimony, "TESTIMONY")
        self.dossier_tabs.addTab(self.tab_contradictions, "CONTRADICTIONS ⚡")
        self.dossier_tabs.addTab(self.tab_interview, "INTERVIEW 💬")

        # Build Interactive Interview Tab
        self._build_interview_tab()

        r_layout.addWidget(self.dossier_tabs, 1)
        content_box.addWidget(right_frame, 1)
        main_layout.addLayout(content_box, 1)

    def _build_interview_tab(self):
        tab_layout = QVBoxLayout(self.tab_interview)
        tab_layout.setContentsMargins(8, 8, 8, 8)
        tab_layout.setSpacing(6)

        lbl_prompt = QLabel("SELECT INTERROGATION LINE OF QUESTIONING:")
        lbl_prompt.setStyleSheet(f"font-size: 11px; font-weight: bold; color: {HEX_GOLD};")
        tab_layout.addWidget(lbl_prompt)

        for q_id, q_text in PREDEFINED_QUESTIONS:
            btn_q = QPushButton(f"• {q_id}: {q_text}")
            btn_q.setStyleSheet("""
                QPushButton {
                    background-color: #2b1b13;
                    border: 1px solid #633c22;
                    text-align: left;
                    padding: 6px 12px;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #4a2c1d;
                    border: 1px solid #ffd741;
                }
            """)
            btn_q.clicked.connect(lambda checked=False, qid=q_id, qtxt=q_text: self._ask_question(qid, qtxt))
            tab_layout.addWidget(btn_q)

        # Response dialogue box
        self.txt_response = QTextBrowser()
        self.txt_response.setStyleSheet("background-color: #1a100b; border: 1px solid #ffd741; border-radius: 6px; padding: 10px; font-size: 13px; line-height: 1.5;")
        self.txt_response.setPlaceholderText("Witness responses and reactions appear here...")
        tab_layout.addWidget(self.txt_response, 1)

    def on_enter_screen(self):
        case = self.game_state.current_case
        if not case:
            return

        self.suspect_list.clear()
        for s in case.suspects:
            item = QListWidgetItem(f"👤 {s.name}\n   {s.occupation}")
            item.setData(Qt.UserRole, s)
            self.suspect_list.addItem(item)

        if self.suspect_list.count() > 0:
            self.suspect_list.setCurrentRow(0)

    def _on_suspect_row_changed(self, row: int):
        if row >= 0:
            item = self.suspect_list.item(row)
            if item:
                suspect = item.data(Qt.UserRole)
                if suspect:
                    self.selected_suspect = suspect
                    self.game_state.selected_suspect_id = suspect.id
                    self._update_suspect_display(suspect)

    def _update_suspect_display(self, s: Suspect):
        self.lbl_suspect_name.setText(s.name.upper())
        self.lbl_suspect_role.setText(f"Occupation: {s.occupation}  |  Relationship: {s.relationship}")

        stress = self.suspect_stress.get(s.id, 20.0)
        self.stress_bar.setValue(int(stress))

        # Avatar update
        self.avatar_widget.set_character(s.avatar_type or "heir", s.name)
        self.avatar_widget.set_expression("calm")

        # Dossier Tabs
        self.tab_profile.setHtml(f"<h3>Background Dossier:</h3><p>{s.occupation} with ties to the victim as {s.relationship}.</p><p>Known Facts: {', '.join(s.known_facts) or 'None recorded.'}</p>")
        self.tab_motive.setHtml(f"<h3>Motive & Financial Circumstance:</h3><p>{s.motive}</p>")
        self.tab_alibi.setHtml(f"<h3>Stated Alibi:</h3><p>{s.alibi}</p>")
        self.tab_testimony.setHtml(f"<h3>Recorded Sworn Statement:</h3><p style='font-style: italic;'>\"{s.statement}\"</p>")

        # Contradictions Tab
        cont_html = "<h3>Forensic Contradictions:</h3>"
        if s.contradictions:
            for c in s.contradictions:
                cont_html += f"<p style='color: #eb3732; font-weight: bold;'>⚡ {c}</p>"
        else:
            cont_html += "<p style='color: #2db955;'>No direct physical contradictions detected against alibi.</p>"
        self.tab_contradictions.setHtml(cont_html)

        self.txt_response.setHtml("<p style='color: #b8a896; font-style: italic;'>Select a question above to interrogate the suspect.</p>")

    def _ask_question(self, q_id: str, q_text: str):
        if not self.selected_suspect:
            return

        suspect = self.selected_suspect
        stress = self.suspect_stress.get(suspect.id, 20.0)

        if q_id == "Q1":  # Whereabouts
            resp = f'"{suspect.alibi}"'
            if suspect.is_guilty or suspect.contradictions:
                self.avatar_widget.set_expression("nervous")
                stress = min(100.0, stress + 35.0)
            else:
                self.avatar_widget.set_expression("calm")
        elif q_id == "Q2":  # Relationship
            resp = f'"{suspect.motive}"'
            self.avatar_widget.set_expression("defensive" if suspect.is_guilty else "calm")
            stress = min(100.0, stress + 15.0)
        elif q_id == "Q3":  # Saw anyone
            resp = f'"{suspect.statement}"'
            self.avatar_widget.set_expression("surprised" if suspect.is_guilty else "calm")
            stress = min(100.0, stress + 10.0)
        elif q_id == "Q4":  # Why present
            resp = f'"I had legitimate business matters concerning my position as {suspect.occupation}."'
            self.avatar_widget.set_expression("calm")
        elif q_id == "Q5":  # Inconsistencies
            if suspect.contradictions:
                resp = f'"That is preposterous! {suspect.contradictions[0]}"'
                self.avatar_widget.set_expression("breakdown" if suspect.is_guilty else "nervous")
                stress = min(100.0, stress + 45.0)
            else:
                resp = '"My statements are completely truthful and verified by physical logs."'
                self.avatar_widget.set_expression("calm")
        else:
            resp = "..."

        self.suspect_stress[suspect.id] = stress
        self.stress_bar.setValue(int(stress))

        tot_sus = len(self.game_state.current_case.suspects) if self.game_state.current_case else 1
        self.game_state.progress.record_suspect_interview(suspect.id, q_id, tot_sus)
        self.save_service.save_active_game(self.game_state)
        self.sound_service.play("typewriter")

        html = f"""
        <p style='color: #ffd741; font-weight: bold;'>Q: {q_text}</p>
        <p style='color: #ffffff; font-size: 13px; font-style: italic;'>{suspect.name}: {resp}</p>
        """
        self.txt_response.setHtml(html)

    def _on_proceed(self):
        self.sound_service.play("click")
        self.proceed_to_board.emit()
        self.navigate.emit("evidence")

