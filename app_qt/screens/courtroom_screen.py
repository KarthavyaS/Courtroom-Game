"""Interactive, Fully Animated AI Courtroom Trial Screen for PySide6 LOGIC COURTROOM.
Modern courtroom chamber with:
- AI Magistrate bench, Advocate podium, and Accused suspect dock
- Animated vector avatars with real-time breathing, blinking, and emotional states
- Golden Scales of Justice swaying with jury persuasion
- Pulsating ECG Discipline Gauge tracking judicial warnings
- Interactive cross-examination: cycling statements, pressing witness, and dramatic objections
- Physical evidence exhibit cards tray for direct interjection
- Deterministic Symbolic AI scoring via ScoringEngine (Backward Chaining, Forward Chaining, Resolution)
"""

from typing import Optional, Dict, Any, List
from PySide6.QtCore import Qt, Signal, QTimer, QRect
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QProgressBar, QScrollArea, QSizePolicy
)

from models.argument import Argument
from models.evidence import Evidence
from services.game_state import GameState
from services.save_service import SaveService
from services.courtroom_session import CourtroomSession
from ai_engine.scoring import ScoringEngine
from app_qt.config import (
    COLOR_BG_CARD, COLOR_BG_PANEL, COLOR_BORDER, COLOR_GOLD, COLOR_GOLD_LIGHT,
    COLOR_GOLD_DARK, COLOR_WHITE, COLOR_TEXT_MUTED, COLOR_TEXT_PARCHMENT,
    COLOR_ACCENT_RED, COLOR_ACCENT_GREEN, COLOR_ACCENT_BLUE, get_qt_font
)
from app_qt.services.sound_service_qt import get_sound_service_qt
from app_qt.widgets.character_avatar import CharacterAvatarQt
from app_qt.widgets.suspect_dock import SuspectDockQt
from app_qt.widgets.dialogue_box import DialogueBoxQt
from app_qt.widgets.scales_of_justice import ScalesOfJusticeQt
from app_qt.widgets.discipline_gauge import DisciplineGaugeQt
from app_qt.dialogs.objection_overlay import ObjectionOverlay
from app_qt.dialogs.wax_seal_overlay import WaxSealOverlay


class CourtroomScreenQt(QWidget):
    """The interactive AI Judge Courtroom trial chamber."""

    navigate = Signal(str)
    notify = Signal(str, str)

    def __init__(self, game_state: GameState, save_service: Optional[SaveService] = None, parent=None):
        super().__init__(parent)
        self.game_state = game_state
        self.save_service = save_service or SaveService()
        self.sound_service = get_sound_service_qt()

        self.session: Optional[CourtroomSession] = None
        self.scoring_engine = ScoringEngine()
        self.evaluation_result: Optional[Dict[str, Any]] = None
        self.is_trial_concluded = False
        self.score_saved = False

        self.jury_persuasion = 50.0
        self.suspect_composure = 100.0
        self.logic_combo = 0

        self.testimony_statements: List[str] = []
        self.current_testimony_idx = 0
        self.evidence_cards: List[QPushButton] = []

        self._init_ui()

        # Overlays
        self.objection_overlay = ObjectionOverlay(self)
        self.wax_seal_overlay = WaxSealOverlay(self)

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 10, 20, 10)
        main_layout.setSpacing(8)

        # 1. Top Section: Header & Live Gauges (Scales of Justice & Discipline ECG)
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(0, 0, 0, 0)

        header_col = QVBoxLayout()
        header_col.setSpacing(2)
        self.lbl_court_title = QLabel("CENTRAL MAGISTRATE CHAMBERS")
        self.lbl_court_title.setFont(get_qt_font(15, bold=True))
        self.lbl_court_title.setStyleSheet(f"color: {COLOR_GOLD.name()}; letter-spacing: 1px;")

        self.lbl_case_docket = QLabel("DOCKET: Formal Pleading Stage")
        self.lbl_case_docket.setFont(get_qt_font(9))
        self.lbl_case_docket.setStyleSheet(f"color: {COLOR_TEXT_PARCHMENT.name()};")
        header_col.addWidget(self.lbl_court_title)
        header_col.addWidget(self.lbl_case_docket)
        top_bar.addLayout(header_col)

        top_bar.addStretch()

        # Center: Scales of Justice
        scales_container = QVBoxLayout()
        scales_container.setSpacing(0)
        scales_container.setAlignment(Qt.AlignCenter)
        self.scales_widget = ScalesOfJusticeQt(self)
        self.lbl_jury_persuasion = QLabel("JURY PERSUASION: 50%")
        self.lbl_jury_persuasion.setFont(get_qt_font(8, bold=True))
        self.lbl_jury_persuasion.setStyleSheet(f"color: {COLOR_GOLD.name()};")
        self.lbl_jury_persuasion.setAlignment(Qt.AlignCenter)
        scales_container.addWidget(self.scales_widget, alignment=Qt.AlignCenter)
        scales_container.addWidget(self.lbl_jury_persuasion, alignment=Qt.AlignCenter)
        top_bar.addLayout(scales_container)

        top_bar.addSpacing(20)

        # Right: Discipline ECG Monitor
        gauge_container = QVBoxLayout()
        gauge_container.setSpacing(0)
        gauge_container.setAlignment(Qt.AlignCenter)
        self.discipline_widget = DisciplineGaugeQt(self)
        self.lbl_discipline = QLabel("JUDICIAL DISCIPLINE: NORMAL")
        self.lbl_discipline.setFont(get_qt_font(8, bold=True))
        self.lbl_discipline.setStyleSheet(f"color: {COLOR_ACCENT_GREEN.name()};")
        self.lbl_discipline.setAlignment(Qt.AlignCenter)
        gauge_container.addWidget(self.discipline_widget, alignment=Qt.AlignCenter)
        gauge_container.addWidget(self.lbl_discipline, alignment=Qt.AlignCenter)
        top_bar.addLayout(gauge_container)

        main_layout.addLayout(top_bar)

        # 2. Stage Section: Characters (Lawyer, Judge Bench, Suspect Dock)
        stage_frame = QFrame()
        stage_frame.setStyleSheet(f"""
            QFrame {{
                background-color: #17110e;
                border: 1px solid {COLOR_BORDER.name()};
                border-radius: 8px;
            }}
        """)
        stage_layout = QHBoxLayout(stage_frame)
        stage_layout.setContentsMargins(16, 8, 16, 8)
        stage_layout.setSpacing(14)

        # Left: Advocate Podium
        podium_box = QVBoxLayout()
        podium_box.setAlignment(Qt.AlignCenter)
        podium_box.setSpacing(4)
        self.avatar_lawyer = CharacterAvatarQt("lawyer", self.game_state.profile.name or "Counsel", self)
        self.avatar_lawyer.setFixedSize(130, 115)
        lbl_lawyer = QLabel("PLAYER COUNSEL")
        lbl_lawyer.setFont(get_qt_font(9, bold=True))
        lbl_lawyer.setStyleSheet(f"color: {COLOR_ACCENT_BLUE.name()};")
        lbl_lawyer.setAlignment(Qt.AlignCenter)
        podium_box.addWidget(self.avatar_lawyer, alignment=Qt.AlignCenter)
        podium_box.addWidget(lbl_lawyer, alignment=Qt.AlignCenter)
        stage_layout.addLayout(podium_box)

        stage_layout.addStretch()

        # Center: Elevated Judge Bench
        bench_box = QVBoxLayout()
        bench_box.setAlignment(Qt.AlignCenter)
        bench_box.setSpacing(4)
        self.avatar_judge = CharacterAvatarQt("judge", "AI Magistrate", self)
        self.avatar_judge.setFixedSize(140, 120)
        lbl_judge = QLabel("AI MAGISTRATE")
        lbl_judge.setFont(get_qt_font(10, bold=True))
        lbl_judge.setStyleSheet(f"color: {COLOR_GOLD.name()};")
        lbl_judge.setAlignment(Qt.AlignCenter)
        bench_box.addWidget(self.avatar_judge, alignment=Qt.AlignCenter)
        bench_box.addWidget(lbl_judge, alignment=Qt.AlignCenter)
        stage_layout.addLayout(bench_box)

        stage_layout.addStretch()

        # Right: Accused Suspect Dock & Composure
        dock_box = QVBoxLayout()
        dock_box.setAlignment(Qt.AlignCenter)
        dock_box.setSpacing(4)
        self.avatar_suspect = CharacterAvatarQt("heir", "The Accused", self)
        self.avatar_suspect.setFixedSize(130, 115)
        self.dock_platform = SuspectDockQt("The Accused", self)
        self.dock_platform.setFixedSize(140, 45)

        comp_row = QHBoxLayout()
        lbl_comp = QLabel("COMPOSURE:")
        lbl_comp.setFont(get_qt_font(8, bold=True))
        lbl_comp.setStyleSheet("color: #ff9999;")
        self.progress_composure = QProgressBar()
        self.progress_composure.setRange(0, 100)
        self.progress_composure.setValue(100)
        self.progress_composure.setFixedSize(80, 8)
        self.progress_composure.setTextVisible(False)
        self.progress_composure.setStyleSheet(f"""
            QProgressBar {{
                background-color: #211512;
                border: 1px solid #4a2222;
                border-radius: 4px;
            }}
            QProgressBar::chunk {{
                background-color: {COLOR_ACCENT_RED.name()};
                border-radius: 3px;
            }}
        """)
        comp_row.addWidget(lbl_comp)
        comp_row.addWidget(self.progress_composure)

        dock_box.addWidget(self.avatar_suspect, alignment=Qt.AlignCenter)
        dock_box.addWidget(self.dock_platform, alignment=Qt.AlignCenter)
        dock_box.addLayout(comp_row)
        stage_layout.addLayout(dock_box)

        main_layout.addWidget(stage_frame)

        # 3. Roomy Dialogue Box
        self.dialogue_box = DialogueBoxQt(self)
        main_layout.addWidget(self.dialogue_box)

        # 4. Interactive Cross-Examination Action Buttons
        self.action_bar = QHBoxLayout()
        self.action_bar.setSpacing(6)

        self.btn_prev_stmt = QPushButton("◀ PREV [Q]")
        self.btn_prev_stmt.setFont(get_qt_font(10, bold=True))
        self.btn_prev_stmt.setStyleSheet("padding: 7px 12px; background-color: #2b1f14; color: #c9a050; border: 1px solid #5a381e; border-radius: 4px;")
        self.btn_prev_stmt.clicked.connect(self._prev_statement)
        self.action_bar.addWidget(self.btn_prev_stmt)

        self.btn_next_stmt = QPushButton("NEXT ▶ [W]")
        self.btn_next_stmt.setFont(get_qt_font(10, bold=True))
        self.btn_next_stmt.setStyleSheet("padding: 7px 12px; background-color: #2b1f14; color: #c9a050; border: 1px solid #5a381e; border-radius: 4px;")
        self.btn_next_stmt.clicked.connect(self._next_statement)
        self.action_bar.addWidget(self.btn_next_stmt)

        self.btn_submit_reading = QPushButton("📖 READ TESTIMONY [SPACE]")
        self.btn_submit_reading.setFont(get_qt_font(10, bold=True))
        self.btn_submit_reading.setStyleSheet("padding: 7px 14px; background-color: #6b4420; color: #ffffff; border: 1px solid #d4af37; border-radius: 4px;")
        self.btn_submit_reading.clicked.connect(self._submit_statement_for_reading)
        self.action_bar.addWidget(self.btn_submit_reading)

        self.btn_press_witness = QPushButton("⚡ PRESS WITNESS [P]")
        self.btn_press_witness.setFont(get_qt_font(10, bold=True))
        self.btn_press_witness.setStyleSheet("padding: 7px 14px; background-color: #7b441a; color: #fff; border: 1px solid #e0a040; border-radius: 4px;")
        self.btn_press_witness.clicked.connect(self._press_current_statement)
        self.action_bar.addWidget(self.btn_press_witness)

        self.btn_objection = QPushButton("💥 OBJECTION! [O]")
        self.btn_objection.setFont(get_qt_font(10, bold=True))
        self.btn_objection.setStyleSheet("padding: 7px 14px; background-color: #8b1e1e; color: #ffffff; border: 1px solid #ff4444; border-radius: 4px;")
        self.btn_objection.clicked.connect(self._trigger_objection)
        self.action_bar.addWidget(self.btn_objection)

        self.btn_watson_hint = QPushButton("💡 WATSON HINT [H]")
        self.btn_watson_hint.setFont(get_qt_font(10, bold=True))
        self.btn_watson_hint.setStyleSheet("padding: 7px 12px; background-color: #1e3a5f; color: #ffffff; border: 1px solid #3a75b4; border-radius: 4px;")
        self.btn_watson_hint.clicked.connect(self._trigger_watson_hint)
        self.action_bar.addWidget(self.btn_watson_hint)

        self.btn_rest_case = QPushButton("⚖ DEMAND VERDICT [R]")
        self.btn_rest_case.setFont(get_qt_font(10, bold=True))
        self.btn_rest_case.setStyleSheet("padding: 7px 16px; background-color: #1e5a1e; color: #ffffff; border: 1px solid #3d8c3d; border-radius: 4px;")
        self.btn_rest_case.clicked.connect(self._conclude_trial)
        self.action_bar.addWidget(self.btn_rest_case)

        main_layout.addLayout(self.action_bar)

        # 5. Bottom Evidence Exhibit Dock / Concluded Panel Stack
        self.bottom_stack = QFrame()
        self.bottom_layout = QVBoxLayout(self.bottom_stack)
        self.bottom_layout.setContentsMargins(0, 0, 0, 0)
        self.bottom_layout.setSpacing(4)

        # Exhibit Tray Container
        self.exhibit_container = QWidget()
        ex_layout = QVBoxLayout(self.exhibit_container)
        ex_layout.setContentsMargins(0, 0, 0, 0)
        ex_layout.setSpacing(4)

        ex_header = QLabel("COURT RECORD EXHIBITS (CLICK EXHIBIT TO PRESENT AS REBUTTAL):")
        ex_header.setFont(get_qt_font(8, bold=True))
        ex_header.setStyleSheet(f"color: {COLOR_GOLD.name()};")
        ex_layout.addWidget(ex_header)

        self.exhibit_cards_layout = QHBoxLayout()
        self.exhibit_cards_layout.setSpacing(8)
        ex_layout.addLayout(self.exhibit_cards_layout)
        self.bottom_layout.addWidget(self.exhibit_container)

        # Verdict / Concluded Container (Initially Hidden)
        self.concluded_container = QFrame()
        self.concluded_container.setStyleSheet(f"""
            QFrame {{
                background-color: #1a120c;
                border: 1px solid {COLOR_GOLD.name()};
                border-radius: 8px;
                padding: 6px;
            }}
        """)
        conc_layout = QHBoxLayout(self.concluded_container)
        conc_layout.setSpacing(10)

        self.lbl_verdict_summary = QLabel("TRIAL CONCLUDED")
        self.lbl_verdict_summary.setFont(get_qt_font(11, bold=True))
        self.lbl_verdict_summary.setStyleSheet("color: #ffffff;")
        conc_layout.addWidget(self.lbl_verdict_summary, stretch=1)

        self.btn_view_results = QPushButton("📜 VIEW RESULTS & METRICS")
        self.btn_view_results.setFont(get_qt_font(10, bold=True))
        self.btn_view_results.setStyleSheet("padding: 8px 16px; background-color: #1e5a1e; color: #fff; border: 1px solid #3d8c3d; border-radius: 4px;")
        self.btn_view_results.clicked.connect(lambda: self.navigate.emit("results"))
        conc_layout.addWidget(self.btn_view_results)

        self.btn_save_score = QPushButton("★ RECORD SCORE")
        self.btn_save_score.setFont(get_qt_font(10, bold=True))
        self.btn_save_score.setStyleSheet("padding: 8px 14px; background-color: #1e3a5f; color: #fff; border: 1px solid #3a75b4; border-radius: 4px;")
        self.btn_save_score.clicked.connect(self._save_score)
        conc_layout.addWidget(self.btn_save_score)

        self.btn_restart_hearing = QPushButton("↺ RESTART HEARING")
        self.btn_restart_hearing.setFont(get_qt_font(10, bold=True))
        self.btn_restart_hearing.setStyleSheet("padding: 8px 14px; background-color: #6b3322; color: #fff; border: 1px solid #c9a050; border-radius: 4px;")
        self.btn_restart_hearing.clicked.connect(self._restart_hearing)
        conc_layout.addWidget(self.btn_restart_hearing)

        self.btn_next_case = QPushButton("SELECT NEXT CASE ➔")
        self.btn_next_case.setFont(get_qt_font(10, bold=True))
        self.btn_next_case.setStyleSheet("padding: 8px 14px; background-color: #3d2b1f; color: #e6d3a3; border: 1px solid #6b4420; border-radius: 4px;")
        self.btn_next_case.clicked.connect(lambda: self.navigate.emit("case_selection"))
        conc_layout.addWidget(self.btn_next_case)

        self.bottom_layout.addWidget(self.concluded_container)
        self.concluded_container.hide()

        main_layout.addWidget(self.bottom_stack)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.objection_overlay.setGeometry(0, 0, self.width(), self.height())
        self.wax_seal_overlay.setGeometry(0, 0, self.width(), self.height())

    def keyPressEvent(self, event):
        key = event.key()
        if not self.is_trial_concluded and (not self.session or not self.session.is_hearing_terminated):
            if key == Qt.Key_Q or key == Qt.Key_Left:
                self._prev_statement()
            elif key == Qt.Key_W or key == Qt.Key_Right:
                self._next_statement()
            elif key == Qt.Key_Space:
                self._submit_statement_for_reading()
            elif key == Qt.Key_P:
                self._press_current_statement()
            elif key == Qt.Key_O:
                self._trigger_objection()
            elif key == Qt.Key_H:
                self._trigger_watson_hint()
            elif key == Qt.Key_R:
                self._conclude_trial()
            else:
                super().keyPressEvent(event)
        else:
            super().keyPressEvent(event)

    def _refresh_session(self):
        suspect = self.game_state.get_selected_suspect()
        if not suspect and self.game_state.current_case and self.game_state.current_case.suspects:
            suspect = self.game_state.current_case.suspects[0]
            self.game_state.selected_suspect_id = suspect.id

        if suspect:
            self.avatar_suspect.set_character(suspect.avatar_type or "heir", suspect.name)
            self.dock_platform.set_suspect_name(suspect.name)
            self.testimony_statements = [
                f'"{suspect.statement}"',
                f'"My alibi is airtight: {suspect.alibi}"',
                f'"I had no reason or motive to be anywhere near the crime scene!"'
            ]
            if suspect.contradictions:
                self.testimony_statements.append('"Any claim that I was seen on cameras or leaving traces is mistaken!"')
        else:
            self.avatar_suspect.set_character("heir", "Unknown Suspect")
            self.dock_platform.set_suspect_name("Unknown Suspect")
            self.testimony_statements = [
                '"I am completely innocent of all allegations brought before the Queen\'s Bench!"',
                '"I was nowhere near the scene at the time of the incident!"'
            ]

        self.current_testimony_idx = 0
        self.jury_persuasion = 50.0
        self.suspect_composure = 100.0
        self.logic_combo = 0
        self.is_trial_concluded = False
        self.score_saved = False

        self.scales_widget.set_persuasion(self.jury_persuasion)
        self.lbl_jury_persuasion.setText(f"JURY PERSUASION: {int(self.jury_persuasion)}%")
        self.progress_composure.setValue(int(self.suspect_composure))

        self.session = CourtroomSession(
            case_data=self.game_state.current_case,
            selected_suspect=suspect
        )

        self._update_discipline_display()
        self._render_evidence_cards()

        self.exhibit_container.show()
        self.concluded_container.hide()

        if self.session.messages:
            first_msg = self.session.messages[0]
            self.dialogue_box.set_message(first_msg.speaker, first_msg.text)
            self.avatar_judge.set_expression("speaking", is_speaking=True)

    def _render_evidence_cards(self):
        while self.exhibit_cards_layout.count() > 0:
            child = self.exhibit_cards_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        self.evidence_cards.clear()

        collected = self.game_state.get_collected_evidence_objects()
        category_icons = {
            "physical": "🗡", "forensic": "🔬", "document": "📄",
            "digital": "💾", "testimonial": "🗣", "alibi": "⏰"
        }

        for ev in collected[:5]:
            icon = category_icons.get(ev.category.lower(), "📂")
            btn = QPushButton(f"{icon} {ev.name}\n[{ev.category.upper()}]")
            btn.setFont(get_qt_font(9, bold=True))
            btn.setFixedHeight(48)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #211713;
                    border: 1px solid #d4af37;
                    border-radius: 6px;
                    color: #ffffff;
                    text-align: center;
                    padding: 4px;
                }
                QPushButton:hover {
                    background-color: #3d2b1f;
                    border-color: #ffd700;
                }
            """)
            btn.clicked.connect(lambda checked=False, e=ev: self._present_evidence_card(e))
            self.evidence_cards.append(btn)
            self.exhibit_cards_layout.addWidget(btn)

        if not collected:
            lbl_none = QLabel("No evidence collected yet. Visit Crime Scene or Evidence Vault.")
            lbl_none.setFont(get_qt_font(9, italic=True))
            lbl_none.setStyleSheet(f"color: {COLOR_TEXT_MUTED.name()};")
            self.exhibit_cards_layout.addWidget(lbl_none)

    def _update_discipline_display(self):
        strikes = self.session.unwanted_argument_count if self.session else 0
        self.discipline_widget.set_strikes(strikes)
        credibility = max(0.0, 100.0 - strikes * 33.3)
        self.discipline_widget.set_credibility(credibility)

        if strikes == 0:
            self.lbl_discipline.setText("JUDICIAL DISCIPLINE: NORMAL")
            self.lbl_discipline.setStyleSheet(f"color: {COLOR_ACCENT_GREEN.name()};")
        elif strikes == 1:
            self.lbl_discipline.setText("JUDICIAL DISCIPLINE: WARNING [1/3]")
            self.lbl_discipline.setStyleSheet(f"color: {COLOR_GOLD.name()};")
        elif strikes == 2:
            self.lbl_discipline.setText("JUDICIAL DISCIPLINE: FINAL WARNING [2/3]")
            self.lbl_discipline.setStyleSheet("color: #ff9944;")
        else:
            self.lbl_discipline.setText("JUDICIAL DISCIPLINE: CONTEMPT [TERMINATED]")
            self.lbl_discipline.setStyleSheet(f"color: {COLOR_ACCENT_RED.name()};")

    def _prev_statement(self):
        if self.testimony_statements:
            self.current_testimony_idx = (self.current_testimony_idx - 1) % len(self.testimony_statements)
            self.sound_service.play("click")
            self._submit_statement_for_reading()

    def _next_statement(self):
        if self.testimony_statements:
            self.current_testimony_idx = (self.current_testimony_idx + 1) % len(self.testimony_statements)
            self.sound_service.play("click")
            self._submit_statement_for_reading()

    def _submit_statement_for_reading(self):
        if not self.testimony_statements:
            return

        suspect = self.game_state.get_selected_suspect()
        s_name = suspect.name if suspect else "Suspect"
        cur_stmt = self.testimony_statements[self.current_testimony_idx % len(self.testimony_statements)]

        self.sound_service.play("dossier")
        self.avatar_suspect.set_expression("speaking", is_speaking=True)
        self.dialogue_box.set_message(s_name, f"TESTIMONY (#{self.current_testimony_idx + 1}): {cur_stmt}")
        self.notify.emit("INFO", f"Entered Statement #{self.current_testimony_idx + 1} into Court Record")

    def _press_current_statement(self):
        if not self.session or self.session.is_hearing_terminated:
            return

        suspect = self.game_state.get_selected_suspect()
        s_name = suspect.name if suspect else "Suspect"

        self.sound_service.play("click")
        self.avatar_lawyer.set_expression("pointing", is_speaking=True)
        self.avatar_suspect.set_expression("nervous")

        self.logic_combo += 1
        dmg = 10.0
        self.suspect_composure = max(0.0, self.suspect_composure - dmg)
        self.jury_persuasion = min(100.0, self.jury_persuasion + 5.0)

        self.progress_composure.setValue(int(self.suspect_composure))
        self.scales_widget.set_persuasion(self.jury_persuasion)
        self.lbl_jury_persuasion.setText(f"JURY PERSUASION: {int(self.jury_persuasion)}%")

        press_responses = [
            f"{s_name}: 'I... well, I was only stepping outside for a breath of fresh evening air!'",
            f"{s_name}: 'Why are you interrogating my exact whereabouts? You have no right!'",
            f"{s_name}: 'I may have passed near the corridor, but I never touched the door lock!'"
        ]
        resp = press_responses[self.current_testimony_idx % len(press_responses)]
        self.dialogue_box.set_message(s_name, resp)
        self.notify.emit("SUCCESS", f"Pressed {s_name}! Composure weakened (-{int(dmg)})")

    def _trigger_objection(self):
        if not self.session or self.session.is_hearing_terminated:
            return

        suspect = self.game_state.get_selected_suspect()
        self.objection_overlay.trigger(text="OBJECTION!", speaker=self.game_state.profile.name)
        self.avatar_lawyer.set_expression("pointing", is_speaking=True)

        if suspect and suspect.contradictions:
            contradiction_arg = f"OBJECTION! {suspect.name}'s statement is directly contradicted: {suspect.contradictions[0]}"
            self._process_argument(contradiction_arg)
        else:
            collected = self.game_state.get_collected_evidence_objects()
            if collected:
                top_ev = collected[0]
                self._process_argument(f"OBJECTION! The court must examine Exhibit {top_ev.id} ({top_ev.name}): {top_ev.description}")
            else:
                self._process_argument("OBJECTION, Your Honor! The accused's timeline contains material factual inconsistencies!")

    def _present_evidence_card(self, ev: Evidence):
        if not self.session or self.session.is_hearing_terminated:
            return

        text = f"OBJECTION! Physical Exhibit {ev.id} ({ev.name}) completely contradicts the testimony: {ev.description}"
        self.objection_overlay.trigger(text="OBJECTION!", speaker=self.game_state.profile.name)
        self.avatar_lawyer.set_expression("pointing", is_speaking=True)

        self.logic_combo += 1
        dmg = 25.0
        self.suspect_composure = max(0.0, self.suspect_composure - dmg)
        self.jury_persuasion = min(100.0, self.jury_persuasion + 15.0)

        self.progress_composure.setValue(int(self.suspect_composure))
        self.scales_widget.set_persuasion(self.jury_persuasion)
        self.lbl_jury_persuasion.setText(f"JURY PERSUASION: {int(self.jury_persuasion)}%")

        self._process_argument(text)

    def _process_argument(self, text: str):
        if not self.session:
            return

        eval_result = self.session.submit_argument(text)

        if eval_result.category == "RELEVANT_SUPPORTED":
            self.jury_persuasion = min(100.0, self.jury_persuasion + 15.0)
            self.suspect_composure = max(0.0, self.suspect_composure - 25.0)
            self.sound_service.play("evidence")
        elif eval_result.category == "RELEVANT_INSUFFICIENT":
            self.jury_persuasion = min(100.0, self.jury_persuasion + 6.0)
            self.suspect_composure = max(0.0, self.suspect_composure - 10.0)
        elif eval_result.is_unwanted:
            self.jury_persuasion = max(0.0, self.jury_persuasion - 15.0)
            self.sound_service.play("warning")

        self.progress_composure.setValue(int(self.suspect_composure))
        self.scales_widget.set_persuasion(self.jury_persuasion)
        self.lbl_jury_persuasion.setText(f"JURY PERSUASION: {int(self.jury_persuasion)}%")

        self.avatar_judge.set_expression(eval_result.judge_expression, is_speaking=True)
        if self.suspect_composure <= 20.0:
            self.avatar_suspect.set_expression("breakdown")
        else:
            self.avatar_suspect.set_expression(eval_result.suspect_expression)

        self.dialogue_box.set_message("Judge", eval_result.judge_dialogue)
        self._update_discipline_display()

        if self.session.is_hearing_terminated:
            self.sound_service.play("gavel")
            self._handle_hearing_terminated()

    def _handle_hearing_terminated(self):
        self.is_trial_concluded = True
        self.lbl_verdict_summary.setText("⚖ HEARING TERMINATED: CONTEMPT OF COURT (3 STRIKES)")
        self.lbl_verdict_summary.setStyleSheet(f"color: {COLOR_ACCENT_RED.name()};")
        self.exhibit_container.hide()
        self.concluded_container.show()
        self.notify.emit("WARNING", "Hearing terminated due to repeated ungrounded pleadings.")

    def _trigger_watson_hint(self):
        self.sound_service.play("evidence")
        unlocked = self.game_state.get_unlocked_facts()

        has_means = any("knife" in f or "weapon" in f or "vault" in f or "signature" in f for f in unlocked)
        has_opp = any("cctv" in f or "present" in f or "opportunity" in f or "entry" in f for f in unlocked)
        has_mot = any("debt" in f or "inheritance" in f or "motive" in f or "fraud" in f for f in unlocked)

        if not has_opp:
            advice = "WATSON: 'Sir! We lack proof of Opportunity! Check the CCTV logs or entry footprints to refute their alibi!'"
        elif not has_means:
            advice = "WATSON: 'Counsel! We need physical proof of Means! Inspect latent fingerprints on the murder weapon or vault!'"
        elif not has_mot:
            advice = "WATSON: 'Clerk Advice: Connect their financial motives or debt messages to establish intent!'"
        else:
            advice = "WATSON: 'Splendid! All legal pillars are substantiated! Request final deliberation now!'"

        self.dialogue_box.set_message("Clerk Watson", advice)
        self.notify.emit("INFO", "Clerk Watson provided investigative advice")

    def _conclude_trial(self):
        if not self.session:
            return

        self.is_trial_concluded = True
        self.sound_service.play("gavel")

        all_premises = []
        if self.session.arguments_submitted:
            for arg_entry in self.session.arguments_submitted:
                if not arg_entry.get("is_unwanted", False):
                    all_premises.append(arg_entry["text"])
        elif self.game_state.current_argument and self.game_state.current_argument.premises:
            all_premises = list(self.game_state.current_argument.premises)
        else:
            all_premises = list(self.game_state.get_unlocked_facts())

        suspect = self.game_state.get_selected_suspect()
        collected_ev = self.game_state.get_collected_evidence_objects()

        final_argument = Argument(
            suspect_id=suspect.id if suspect else "SUS-001",
            premises=all_premises,
            conclusion=self.game_state.current_case.solution_conclusion if self.game_state.current_case else "suspect_guilty_beyond_reasonable_doubt",
            selected_evidence_ids=[e.id for e in collected_ev]
        )

        self.evaluation_result = self.scoring_engine.evaluate_argument(
            argument=final_argument,
            kb=self.session.kb,
            collected_evidence=collected_ev,
            suspect=suspect
        )

        base_score = self.evaluation_result.get("total_score", 0)
        final_score = max(0, min(100, base_score + self.session.cumulative_score))
        self.evaluation_result["total_score"] = final_score
        self.game_state.last_verdict_result = self.evaluation_result

        self.game_state.profile.arguments_submitted += len(self.session.arguments_submitted)
        self.game_state.profile.cases_completed += 1
        self.game_state.profile.highest_score = max(self.game_state.profile.highest_score, final_score)

        is_won = self.evaluation_result["verdict"] == "SUPPORTED"
        if is_won:
            self.game_state.profile.cases_won += 1
            self.game_state.profile.total_score += final_score
            self.avatar_judge.set_expression("satisfied")
            self.avatar_suspect.set_expression("nervous")
            self.wax_seal_overlay.trigger(text="PROVEN BEYOND DOUBT", is_won=True)
            self.lbl_verdict_summary.setText(f"⚖ VERDICT: GUILT PROVEN! Score: {final_score}/100")
            self.lbl_verdict_summary.setStyleSheet(f"color: {COLOR_ACCENT_GREEN.name()};")
        else:
            self.game_state.profile.total_score += final_score
            self.avatar_judge.set_expression("thinking")
            self.avatar_suspect.set_expression("surprised")
            self.wax_seal_overlay.trigger(text="INSUFFICIENT PROOF", is_won=False)
            self.lbl_verdict_summary.setText(f"⚖ VERDICT: {self.evaluation_result['verdict']}. Score: {final_score}/100")
            self.lbl_verdict_summary.setStyleSheet(f"color: {COLOR_GOLD.name()};")

        self.save_service.save_profile(self.game_state.profile)

        self.exhibit_container.hide()
        self.concluded_container.show()
        self.notify.emit("SUCCESS" if is_won else "WARNING", f"Trial Concluded! Final Score: {final_score}/100")

    def _restart_hearing(self):
        self.is_trial_concluded = False
        self.score_saved = False
        self.evaluation_result = None
        if self.session:
            self.session.restart_hearing()
            if self.session.messages:
                first_msg = self.session.messages[0]
                self.dialogue_box.set_message(first_msg.speaker, first_msg.text)
        self.jury_persuasion = 50.0
        self.suspect_composure = 100.0
        self.scales_widget.set_persuasion(50.0)
        self.lbl_jury_persuasion.setText("JURY PERSUASION: 50%")
        self.progress_composure.setValue(100)
        self._update_discipline_display()
        self.exhibit_container.show()
        self.concluded_container.hide()
        self.notify.emit("INFO", "Hearing restarted. Penalties reset.")

    def _save_score(self):
        if self.score_saved or not self.evaluation_result or not self.game_state.current_case:
            return
        success = self.save_service.record_score(
            player_name=self.game_state.profile.name,
            case_id=self.game_state.current_case.id,
            case_title=self.game_state.current_case.title,
            score=self.evaluation_result["total_score"],
            verdict=self.evaluation_result["verdict"]
        )
        if success:
            self.score_saved = True
            self.sound_service.play("evidence")
            self.notify.emit("SUCCESS", "Score recorded to Hall of Fame!")

    def on_enter_screen(self):
        """Called when this screen becomes active."""
        if self.game_state.current_case:
            self.lbl_case_docket.setText(f"DOCKET: Case #{self.game_state.current_case.id} - {self.game_state.current_case.title}")
        self._refresh_session()

