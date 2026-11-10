"""Verdict and Results Screen for PySide6 LOGIC COURTROOM.
Presents the detailed post-trial ruling delivered by the AI Judge:
- Final case outcome (SUPPORTED / NOT PROVEN / CONTRADICTED) with clear logical meaning.
- Detailed score breakdown (Quality, Evidence, Logic, Discipline).
- Comprehensive judicial feedback and derivation metrics from Forward Chaining and Resolution.
- Actions: Review Hearing, Review Case, Play Another Case, and Return to Dashboard.
"""

from typing import Optional, Dict, Any
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QSizePolicy
)

from services.game_state import GameState
from services.save_service import SaveService
from app_qt.config import (
    COLOR_BG_CARD, COLOR_BG_PANEL, COLOR_BORDER, COLOR_GOLD, COLOR_GOLD_LIGHT,
    COLOR_GOLD_DARK, COLOR_WHITE, COLOR_TEXT_MUTED, COLOR_TEXT_PARCHMENT,
    COLOR_ACCENT_GREEN, COLOR_ACCENT_RED, COLOR_ACCENT_BLUE, get_qt_font
)
from app_qt.services.sound_service_qt import get_sound_service_qt
from app_qt.dialogs.wax_seal_overlay import WaxSealOverlay


class ResultsScreenQt(QWidget):
    """Post-trial verdict and judicial assessment screen."""

    navigate = Signal(str)
    notify = Signal(str, str)

    def __init__(self, game_state: GameState, save_service: Optional[SaveService] = None, parent=None):
        super().__init__(parent)
        self.game_state = game_state
        self.save_service = save_service or SaveService()
        self.sound_service = get_sound_service_qt()

        self._init_ui()
        self.wax_seal_overlay = WaxSealOverlay(self)

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 16, 24, 16)
        main_layout.setSpacing(12)

        # 1. Header Bar
        header_layout = QHBoxLayout()
        title_lbl = QLabel("COURT OF QUEEN'S BENCH — OFFICIAL VERDICT & DECREE")
        title_lbl.setFont(get_qt_font(16, bold=True))
        title_lbl.setStyleSheet(f"color: {COLOR_GOLD.name()}; letter-spacing: 1px;")
        header_layout.addWidget(title_lbl)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)

        # 2. Outcome Banner
        self.banner_frame = QFrame()
        self.banner_frame.setFixedHeight(80)
        ban_layout = QHBoxLayout(self.banner_frame)
        ban_layout.setContentsMargins(20, 12, 20, 12)

        ban_text_col = QVBoxLayout()
        ban_text_col.setSpacing(2)
        self.lbl_verdict_title = QLabel("VERDICT: ARGUMENT SUPPORTED")
        self.lbl_verdict_title.setFont(get_qt_font(15, bold=True))

        self.lbl_verdict_sub = QLabel("The supplied premises logically entail the conclusion through sound deduction.")
        self.lbl_verdict_sub.setFont(get_qt_font(10))
        self.lbl_verdict_sub.setStyleSheet(f"color: {COLOR_TEXT_PARCHMENT.name()};")
        ban_text_col.addWidget(self.lbl_verdict_title)
        ban_text_col.addWidget(self.lbl_verdict_sub)
        ban_layout.addLayout(ban_text_col)

        ban_layout.addStretch()

        self.lbl_verdict_score = QLabel("+100 PTS")
        self.lbl_verdict_score.setFont(get_qt_font(20, bold=True))
        self.lbl_verdict_score.setStyleSheet(f"color: {COLOR_GOLD.name()};")
        ban_layout.addWidget(self.lbl_verdict_score)

        main_layout.addWidget(self.banner_frame)

        # 3. Two-Column Body Layout
        body_layout = QHBoxLayout()
        body_layout.setSpacing(14)

        # Left Column: Judicial Inference Summary & Trace
        left_frame = QFrame()
        left_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLOR_BG_CARD.name()};
                border: 1px solid {COLOR_BORDER.name()};
                border-radius: 8px;
            }}
        """)
        left_layout = QVBoxLayout(left_frame)
        left_layout.setContentsMargins(18, 16, 18, 16)
        left_layout.setSpacing(10)

        c1_title = QLabel("JUDICIAL INFERENCE SUMMARY")
        c1_title.setFont(get_qt_font(12, bold=True))
        c1_title.setStyleSheet(f"color: {COLOR_GOLD.name()};")
        left_layout.addWidget(c1_title)

        self.lbl_reasoning = QLabel()
        self.lbl_reasoning.setFont(get_qt_font(10))
        self.lbl_reasoning.setWordWrap(True)
        self.lbl_reasoning.setStyleSheet(f"color: {COLOR_WHITE.name()}; line-height: 140%;")
        left_layout.addWidget(self.lbl_reasoning)

        left_layout.addStretch()

        # AI Engine Derivation Metrics Box
        trace_frame = QFrame()
        trace_frame.setStyleSheet("background-color: #17110e; border: 1px solid #3d2b1f; border-radius: 6px; padding: 10px;")
        tr_layout = QVBoxLayout(trace_frame)
        tr_layout.setSpacing(4)

        tr_title = QLabel("AI ENGINE DERIVATION METRICS:")
        tr_title.setFont(get_qt_font(10, bold=True))
        tr_title.setStyleSheet(f"color: {COLOR_GOLD.name()};")
        tr_layout.addWidget(tr_title)

        self.lbl_trace_1 = QLabel("• Forward Chaining: Entailment verified across KnowledgeBase")
        self.lbl_trace_1.setFont(get_qt_font(9))
        self.lbl_trace_1.setStyleSheet(f"color: {COLOR_TEXT_PARCHMENT.name()};")
        tr_layout.addWidget(self.lbl_trace_1)

        self.lbl_trace_2 = QLabel("• Propositional Resolution: Refutation graph closed with empty clause")
        self.lbl_trace_2.setFont(get_qt_font(9))
        self.lbl_trace_2.setStyleSheet(f"color: {COLOR_TEXT_PARCHMENT.name()};")
        tr_layout.addWidget(self.lbl_trace_2)

        self.lbl_trace_3 = QLabel("• Fallacy Safeguards: Non-sequitur and circularity checks passed")
        self.lbl_trace_3.setFont(get_qt_font(9))
        self.lbl_trace_3.setStyleSheet(f"color: {COLOR_TEXT_PARCHMENT.name()};")
        tr_layout.addWidget(self.lbl_trace_3)

        self.lbl_trace_4 = QLabel("• Relevant Statements: Supported and logged in court transcript")
        self.lbl_trace_4.setFont(get_qt_font(9))
        self.lbl_trace_4.setStyleSheet(f"color: {COLOR_TEXT_PARCHMENT.name()};")
        tr_layout.addWidget(self.lbl_trace_4)

        left_layout.addWidget(trace_frame)
        body_layout.addWidget(left_frame, stretch=3)

        # Right Column: Performance Evaluation
        right_frame = QFrame()
        right_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLOR_BG_CARD.name()};
                border: 1px solid {COLOR_BORDER.name()};
                border-radius: 8px;
            }}
        """)
        right_layout = QVBoxLayout(right_frame)
        right_layout.setContentsMargins(18, 16, 18, 16)
        right_layout.setSpacing(8)

        c2_title = QLabel("PERFORMANCE EVALUATION")
        c2_title.setFont(get_qt_font(12, bold=True))
        c2_title.setStyleSheet(f"color: {COLOR_GOLD.name()};")
        right_layout.addWidget(c2_title)

        self.lbl_metric_logic = self._create_metric_row("Logical Entailment Validity", "95%", right_layout)
        self.lbl_metric_evidence = self._create_metric_row("Evidence Collection Completeness", "4 Clues", right_layout)
        self.lbl_metric_discipline = self._create_metric_row("Court Discipline & Relevance", "3/3 Strikes", right_layout)
        self.lbl_metric_suspects = self._create_metric_row("Suspect Interrogation Depth", "3 Suspects", right_layout)

        right_layout.addStretch()

        # Recommendation box
        rec_frame = QFrame()
        rec_frame.setStyleSheet(f"background-color: #172817; border: 1px solid {COLOR_ACCENT_GREEN.name()}; border-radius: 6px; padding: 10px;")
        rec_layout = QVBoxLayout(rec_frame)
        rec_layout.setSpacing(3)

        rec_title = QLabel("RECOMMENDATION FOR FUTURE CASES:")
        rec_title.setFont(get_qt_font(9, bold=True))
        rec_title.setStyleSheet(f"color: {COLOR_ACCENT_GREEN.name()};")
        rec_layout.addWidget(rec_title)

        rec_desc = QLabel("Always verify physical evidence against stated suspect alibis before submitting your final argument.")
        rec_desc.setFont(get_qt_font(9))
        rec_desc.setWordWrap(True)
        rec_desc.setStyleSheet(f"color: {COLOR_WHITE.name()};")
        rec_layout.addWidget(rec_desc)

        right_layout.addWidget(rec_frame)
        body_layout.addWidget(right_frame, stretch=2)

        main_layout.addLayout(body_layout, stretch=1)

        # 4. Bottom Action Buttons Bar
        btn_bar = QHBoxLayout()
        btn_bar.setSpacing(12)

        btn_review_hearing = QPushButton("📜 REVIEW HEARING")
        btn_review_hearing.setFont(get_qt_font(10, bold=True))
        btn_review_hearing.setFixedHeight(40)
        btn_review_hearing.setStyleSheet("background-color: #2b1f14; color: #c9a050; border: 1px solid #5a381e; border-radius: 4px;")
        btn_review_hearing.clicked.connect(lambda: self.navigate.emit("courtroom"))
        btn_bar.addWidget(btn_review_hearing)

        btn_review_case = QPushButton("📁 REVIEW CASE FILE")
        btn_review_case.setFont(get_qt_font(10, bold=True))
        btn_review_case.setFixedHeight(40)
        btn_review_case.setStyleSheet("background-color: #3d2b1f; color: #e6d3a3; border: 1px solid #6b4420; border-radius: 4px;")
        btn_review_case.clicked.connect(lambda: self.navigate.emit("case_briefing"))
        btn_bar.addWidget(btn_review_case)

        btn_play_another = QPushButton("📂 PLAY ANOTHER CASE")
        btn_play_another.setFont(get_qt_font(10, bold=True))
        btn_play_another.setFixedHeight(40)
        btn_play_another.setStyleSheet("background-color: #6b4420; color: #fff; border: 1px solid #d4af37; border-radius: 4px;")
        btn_play_another.clicked.connect(lambda: self.navigate.emit("case_selection"))
        btn_bar.addWidget(btn_play_another)

        btn_dashboard = QPushButton("⌂ RETURN TO HUB")
        btn_dashboard.setFont(get_qt_font(10, bold=True))
        btn_dashboard.setFixedHeight(40)
        btn_dashboard.setStyleSheet(f"background-color: {COLOR_ACCENT_GREEN.name()}; color: #fff; border: 1px solid #3d8c3d; border-radius: 4px;")
        btn_dashboard.clicked.connect(lambda: self.navigate.emit("dashboard"))
        btn_bar.addWidget(btn_dashboard)

        main_layout.addLayout(btn_bar)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.wax_seal_overlay.setGeometry(0, 0, self.width(), self.height())

    def _create_metric_row(self, title: str, default_val: str, parent_layout: QVBoxLayout) -> QLabel:
        frame = QFrame()
        frame.setStyleSheet("background-color: #1a120c; border: 1px solid #3d2b1f; border-radius: 4px; padding: 6px;")
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(8, 4, 8, 4)

        lbl_t = QLabel(title)
        lbl_t.setFont(get_qt_font(9))
        lbl_t.setStyleSheet(f"color: {COLOR_TEXT_PARCHMENT.name()};")
        layout.addWidget(lbl_t)

        lbl_v = QLabel(default_val)
        lbl_v.setFont(get_qt_font(10, bold=True))
        lbl_v.setStyleSheet(f"color: {COLOR_GOLD.name()};")
        layout.addWidget(lbl_v, alignment=Qt.AlignRight)

        parent_layout.addWidget(frame)
        return lbl_v

    def on_enter_screen(self):
        """Refreshes results display with last verdict result."""
        verdict_data = self.game_state.last_verdict_result or {}
        outcome = verdict_data.get("verdict") or verdict_data.get("status") or "SUPPORTED"
        score = verdict_data.get("total_score", verdict_data.get("score", 100))
        is_won = (outcome == "SUPPORTED")

        # Update Banner
        if is_won:
            self.banner_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: #183318;
                    border: 2px solid {COLOR_ACCENT_GREEN.name()};
                    border-radius: 8px;
                }}
            """)
            self.lbl_verdict_title.setText("VERDICT: ARGUMENT SUPPORTED (PROVEN BEYOND DOUBT)")
            self.lbl_verdict_title.setStyleSheet(f"color: {COLOR_ACCENT_GREEN.name()};")
            self.lbl_verdict_sub.setText("The supplied premises logically entail the conclusion through sound deduction.")
            self.lbl_verdict_score.setText(f"+{score} PTS")
            self.lbl_verdict_score.setStyleSheet(f"color: {COLOR_ACCENT_GREEN.name()};")
            self.wax_seal_overlay.trigger(text="PROVEN", is_won=True)
        elif outcome == "CONTRADICTED":
            self.banner_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: #331818;
                    border: 2px solid {COLOR_ACCENT_RED.name()};
                    border-radius: 8px;
                }}
            """)
            self.lbl_verdict_title.setText("VERDICT: CONTRADICTED BY EVIDENCE")
            self.lbl_verdict_title.setStyleSheet(f"color: {COLOR_ACCENT_RED.name()};")
            self.lbl_verdict_sub.setText("Physical evidence or established case rules directly refute the argument.")
            self.lbl_verdict_score.setText(f"+{score} PTS")
            self.lbl_verdict_score.setStyleSheet(f"color: {COLOR_ACCENT_RED.name()};")
            self.wax_seal_overlay.trigger(text="CONTRADICTED", is_won=False)
        else:
            self.banner_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: #332814;
                    border: 2px solid {COLOR_GOLD.name()};
                    border-radius: 8px;
                }}
            """)
            self.lbl_verdict_title.setText("VERDICT: NOT PROVEN (INSUFFICIENT PROPOSITIONS)")
            self.lbl_verdict_title.setStyleSheet(f"color: {COLOR_GOLD.name()};")
            self.lbl_verdict_sub.setText("The deduction is plausible, but missing key physical evidence to achieve conviction.")
            self.lbl_verdict_score.setText(f"+{score} PTS")
            self.lbl_verdict_score.setStyleSheet(f"color: {COLOR_GOLD.name()};")
            self.wax_seal_overlay.trigger(text="NOT PROVEN", is_won=False)

        # Reasoning
        reasoning = verdict_data.get("feedback") or verdict_data.get("reasoning") or "Deductive inference rules were executed across all available facts and premises."
        self.lbl_reasoning.setText(f"Judicial Finding:\n{reasoning}")

        # Metrics
        self.lbl_metric_logic.setText(f"{score}% Score")
        self.lbl_metric_evidence.setText(f"{len(self.game_state.collected_evidence_ids)} Clues")
        self.lbl_metric_discipline.setText(f"{max(0, 3 - getattr(self.game_state, 'warning_count', 0))}/3 Warning Pips")
        self.lbl_metric_suspects.setText(f"{len(self.game_state.progress.interviewed_suspect_ids)} Interviewed")

        # Record progress and clear active save
        self.game_state.progress.record_courtroom_finished()
        self.save_service.clear_active_save()

