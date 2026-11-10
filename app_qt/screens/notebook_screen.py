"""Personal Investigation Notebook Screen for PySide6 LOGIC COURTROOM.
Serves as the player's personal detective binder with 4 tabs:
- Tab 1: Case Overview & Target Legal Objective
- Tab 2: Suspect Dossiers & Contradictions
- Tab 3: Discovered & Collected Forensic Evidence Log
- Tab 4: Player Scratchpad Notes (editable with auto-save)
"""

from typing import Optional
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QTabWidget, QTextEdit, QScrollArea, QSizePolicy
)

from services.game_state import GameState
from services.save_service import SaveService
from app_qt.config import (
    COLOR_BG_CARD, COLOR_BG_PANEL, COLOR_BORDER, COLOR_GOLD, COLOR_GOLD_LIGHT,
    COLOR_WHITE, COLOR_TEXT_MUTED, COLOR_TEXT_PARCHMENT, COLOR_ACCENT_GREEN,
    COLOR_ACCENT_RED, get_qt_font
)
from app_qt.services.sound_service_qt import get_sound_service_qt


class NotebookScreenQt(QWidget):
    """Personal detective notebook with editable notes and case reference logs."""

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
        main_layout.setContentsMargins(24, 16, 24, 16)
        main_layout.setSpacing(12)

        # 1. Top Header
        header_layout = QHBoxLayout()

        title_col = QVBoxLayout()
        title_col.setSpacing(2)
        title_lbl = QLabel("DETECTIVE'S FIELD NOTEBOOK")
        title_lbl.setFont(get_qt_font(18, bold=True))
        title_lbl.setStyleSheet(f"color: {COLOR_GOLD.name()}; letter-spacing: 1px;")

        sub_lbl = QLabel("Review collected intelligence, suspect alibis, and record personal trial strategies.")
        sub_lbl.setFont(get_qt_font(10))
        sub_lbl.setStyleSheet(f"color: {COLOR_TEXT_MUTED.name()};")
        title_col.addWidget(title_lbl)
        title_col.addWidget(sub_lbl)
        header_layout.addLayout(title_col)

        header_layout.addStretch()

        self.btn_proceed = QPushButton("PREPARE ARGUMENTS ➔")
        self.btn_proceed.setFont(get_qt_font(11, bold=True))
        self.btn_proceed.setStyleSheet("padding: 8px 18px; background-color: #8b2500; color: #fff; border: 1px solid #d4af37; border-radius: 4px;")
        self.btn_proceed.clicked.connect(self._on_proceed_clicked)
        header_layout.addWidget(self.btn_proceed)

        main_layout.addLayout(header_layout)

        # 2. Tabs Container
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                background-color: {COLOR_BG_CARD.name()};
                border: 1px solid {COLOR_BORDER.name()};
                border-radius: 8px;
            }}
            QTabBar::tab {{
                background-color: #1a120c;
                color: #a08c70;
                padding: 8px 22px;
                margin-right: 4px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                border: 1px solid #3d2b1f;
                font-weight: bold;
            }}
            QTabBar::tab:selected {{
                background-color: {COLOR_BG_CARD.name()};
                color: {COLOR_GOLD.name()};
                border-bottom: 2px solid {COLOR_GOLD.name()};
            }}
            QTabBar::tab:hover:!selected {{
                background-color: #2b1f14;
                color: #e6d3a3;
            }}
        """)
        self.tabs.currentChanged.connect(lambda idx: self.sound_service.play("click"))

        # Tab 1: Overview
        self.tab_overview = QWidget()
        self._init_overview_tab(self.tab_overview)
        self.tabs.addTab(self.tab_overview, "CASE DOSSIER")

        # Tab 2: Suspects
        self.tab_suspects = QWidget()
        self._init_suspects_tab(self.tab_suspects)
        self.tabs.addTab(self.tab_suspects, "SUSPECTS & ALIBIS")

        # Tab 3: Evidence Log
        self.tab_evidence = QWidget()
        self._init_evidence_tab(self.tab_evidence)
        self.tabs.addTab(self.tab_evidence, "EVIDENCE LOG")

        # Tab 4: Player Notes
        self.tab_notes = QWidget()
        self._init_notes_tab(self.tab_notes)
        self.tabs.addTab(self.tab_notes, "MY NOTES ✍")

        main_layout.addWidget(self.tabs, stretch=1)

    def _init_overview_tab(self, parent: QWidget):
        layout = QVBoxLayout(parent)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        self.lbl_case_title = QLabel("CASE OVERVIEW")
        self.lbl_case_title.setFont(get_qt_font(14, bold=True))
        self.lbl_case_title.setStyleSheet(f"color: {COLOR_GOLD.name()};")
        layout.addWidget(self.lbl_case_title)

        self.lbl_case_meta = QLabel("Category • Location")
        self.lbl_case_meta.setFont(get_qt_font(10))
        self.lbl_case_meta.setStyleSheet(f"color: {COLOR_TEXT_PARCHMENT.name()};")
        layout.addWidget(self.lbl_case_meta)

        # Narrative Frame
        narrative_frame = QFrame()
        narrative_frame.setStyleSheet("background-color: #1a120c; border: 1px solid #3d2b1f; border-radius: 6px; padding: 12px;")
        narrative_layout = QVBoxLayout(narrative_frame)
        self.lbl_description = QLabel()
        self.lbl_description.setFont(get_qt_font(11))
        self.lbl_description.setWordWrap(True)
        self.lbl_description.setStyleSheet(f"color: {COLOR_WHITE.name()}; line-height: 140%;")
        narrative_layout.addWidget(self.lbl_description)
        layout.addWidget(narrative_frame)

        # Target Legal Proposition Target
        target_frame = QFrame()
        target_frame.setStyleSheet(f"background-color: #182818; border: 1px solid {COLOR_ACCENT_GREEN.name()}; border-radius: 6px; padding: 12px;")
        t_layout = QVBoxLayout(target_frame)
        t_layout.setSpacing(4)

        target_badge = QLabel("LEGAL PROPOSITION TARGET:")
        target_badge.setFont(get_qt_font(10, bold=True))
        target_badge.setStyleSheet(f"color: {COLOR_ACCENT_GREEN.name()};")
        t_layout.addWidget(target_badge)

        self.lbl_target_conclusion = QLabel()
        self.lbl_target_conclusion.setFont(get_qt_font(13, bold=True))
        self.lbl_target_conclusion.setStyleSheet(f"color: {COLOR_WHITE.name()};")
        t_layout.addWidget(self.lbl_target_conclusion)

        target_hint = QLabel("Must be formally proven before the AI Judge using forward inference rules and indisputable evidence.")
        target_hint.setFont(get_qt_font(9))
        target_hint.setStyleSheet(f"color: {COLOR_TEXT_PARCHMENT.name()};")
        t_layout.addWidget(target_hint)

        layout.addWidget(target_frame)
        layout.addStretch()

    def _init_suspects_tab(self, parent: QWidget):
        layout = QVBoxLayout(parent)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(10)

        header = QLabel("PERSONS OF INTEREST & RECORDED STATEMENTS")
        header.setFont(get_qt_font(13, bold=True))
        header.setStyleSheet(f"color: {COLOR_GOLD.name()};")
        layout.addWidget(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background-color: transparent; border: none;")

        self.suspects_container = QWidget()
        self.suspects_layout = QVBoxLayout(self.suspects_container)
        self.suspects_layout.setSpacing(10)
        self.suspects_layout.addStretch()

        scroll.setWidget(self.suspects_container)
        layout.addWidget(scroll)

    def _init_evidence_tab(self, parent: QWidget):
        layout = QVBoxLayout(parent)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(10)

        self.lbl_evidence_header = QLabel("FORENSIC LOG")
        self.lbl_evidence_header.setFont(get_qt_font(13, bold=True))
        self.lbl_evidence_header.setStyleSheet(f"color: {COLOR_GOLD.name()};")
        layout.addWidget(self.lbl_evidence_header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background-color: transparent; border: none;")

        self.evidence_container = QWidget()
        self.evidence_layout = QVBoxLayout(self.evidence_container)
        self.evidence_layout.setSpacing(10)
        self.evidence_layout.addStretch()

        scroll.setWidget(self.evidence_container)
        layout.addWidget(scroll)

    def _init_notes_tab(self, parent: QWidget):
        layout = QVBoxLayout(parent)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(10)

        header = QLabel("PERSONAL INVESTIGATION SCRATCHPAD")
        header.setFont(get_qt_font(13, bold=True))
        header.setStyleSheet(f"color: {COLOR_GOLD.name()};")
        layout.addWidget(header)

        sub = QLabel("Record your theories, suspect motives, and trial strategies here. Auto-saved across sessions.")
        sub.setFont(get_qt_font(9))
        sub.setStyleSheet(f"color: {COLOR_TEXT_PARCHMENT.name()};")
        layout.addWidget(sub)

        self.txt_notes = QTextEdit()
        self.txt_notes.setFont(get_qt_font(11))
        self.txt_notes.setPlaceholderText("Type your personal observations, theories, and notes here (auto-saved)...")
        self.txt_notes.setStyleSheet(f"""
            QTextEdit {{
                background-color: #17110e;
                color: #e6d3a3;
                border: 1px solid #3d2b1f;
                border-radius: 6px;
                padding: 10px;
                line-height: 140%;
            }}
            QTextEdit:focus {{
                border: 1px solid {COLOR_GOLD.name()};
            }}
        """)
        layout.addWidget(self.txt_notes, stretch=1)

        btn_bar = QHBoxLayout()
        btn_bar.addStretch()

        btn_save = QPushButton("SAVE NOTES 💾")
        btn_save.setFont(get_qt_font(10, bold=True))
        btn_save.setStyleSheet("padding: 8px 18px; background-color: #1e4a1e; color: #fff; border: 1px solid #3d8c3d; border-radius: 4px;")
        btn_save.clicked.connect(self._save_notes)
        btn_bar.addWidget(btn_save)

        layout.addLayout(btn_bar)

    def _save_notes(self):
        text = self.txt_notes.toPlainText()
        self.game_state.progress.player_notes = text
        self.save_service.save_active_game(self.game_state)
        self.sound_service.play("type")
        self.notify.emit("SUCCESS", "Detective notes saved successfully!")

    def _on_proceed_clicked(self):
        self.sound_service.play("click")
        self.navigate.emit("arguments")

    def on_enter_screen(self):
        """Refreshes tab contents with the latest game state."""
        case = self.game_state.current_case
        if not case:
            return

        # 1. Overview Tab
        self.lbl_case_title.setText(f"CASE OVERVIEW: {case.title.upper()} ({case.id})")
        self.lbl_case_meta.setText(f"Category: {case.type}  •  Crime Scene: {case.scene_name}")
        self.lbl_description.setText(case.description)
        self.lbl_target_conclusion.setText(f"\"{case.solution_conclusion}\"")

        # 2. Suspects Tab
        # Clear previous items
        while self.suspects_layout.count() > 1:
            child = self.suspects_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        for s in case.suspects:
            s_frame = QFrame()
            s_frame.setStyleSheet("background-color: #1a120c; border: 1px solid #3d2b1f; border-radius: 6px; padding: 10px;")
            s_layout = QVBoxLayout(s_frame)
            s_layout.setSpacing(4)

            name_lbl = QLabel(f"👤 {s.name}  —  {s.occupation}")
            name_lbl.setFont(get_qt_font(11, bold=True))
            name_lbl.setStyleSheet(f"color: {COLOR_GOLD.name()};")
            s_layout.addWidget(name_lbl)

            alibi_lbl = QLabel(f"Alibi: {s.alibi}")
            alibi_lbl.setFont(get_qt_font(10))
            alibi_lbl.setStyleSheet(f"color: {COLOR_WHITE.name()};")
            s_layout.addWidget(alibi_lbl)

            stat_lbl = QLabel(f"Statement: \"{s.statement}\"")
            stat_lbl.setFont(get_qt_font(9))
            stat_lbl.setWordWrap(True)
            stat_lbl.setStyleSheet(f"color: {COLOR_TEXT_PARCHMENT.name()};")
            s_layout.addWidget(stat_lbl)

            self.suspects_layout.insertWidget(self.suspects_layout.count() - 1, s_frame)

        # 3. Evidence Tab
        while self.evidence_layout.count() > 1:
            child = self.evidence_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        coll_ids = set(self.game_state.collected_evidence_ids)
        self.lbl_evidence_header.setText(f"FORENSIC LOG ({len(coll_ids)} Collected)")

        for ev in case.evidence_list:
            is_coll = ev.id in coll_ids
            e_frame = QFrame()
            bg_col = "#182818" if is_coll else "#1a120c"
            bdr_col = COLOR_ACCENT_GREEN.name() if is_coll else "#3d2b1f"
            e_frame.setStyleSheet(f"background-color: {bg_col}; border: 1px solid {bdr_col}; border-radius: 6px; padding: 10px;")
            e_layout = QVBoxLayout(e_frame)
            e_layout.setSpacing(3)

            status_str = "[COLLECTED ✓]" if is_coll else "[NOT COLLECTED]"
            stat_col = COLOR_GOLD.name() if is_coll else COLOR_TEXT_MUTED.name()
            e_header = QLabel(f"🔍 {ev.name} — {status_str}")
            e_header.setFont(get_qt_font(11, bold=True))
            e_header.setStyleSheet(f"color: {stat_col};")
            e_layout.addWidget(e_header)

            unlocked = getattr(ev, "unlocked_facts", None) or getattr(ev, "facts_unlocked", [])
            meta_str = f"Category: {ev.category}  •  Reliability: {int(ev.reliability * 100)}%  •  Unlocks: {', '.join(unlocked) if unlocked else 'None'}"
            e_meta = QLabel(meta_str)
            e_meta.setFont(get_qt_font(9))
            e_meta.setStyleSheet(f"color: {COLOR_TEXT_PARCHMENT.name()};")
            e_layout.addWidget(e_meta)

            self.evidence_layout.insertWidget(self.evidence_layout.count() - 1, e_frame)

        # 4. Notes Tab
        self.txt_notes.setPlainText(self.game_state.progress.player_notes or "")

