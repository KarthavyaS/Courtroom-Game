"""Create Case Screen for PySide6 LOGIC COURTROOM.
Allows players to author, validate, and publish custom fictional investigation cases.
"""

import uuid
from typing import Optional
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTextEdit, QComboBox, QFrame, QScrollArea, QSizePolicy
)

from models.case import Case
from models.suspect import Suspect
from models.evidence import Evidence
from services.case_service import CaseService
from services.game_state import GameState
from services.save_service import SaveService
from app_qt.config import (
    COLOR_BG_CARD, COLOR_BG_PANEL, COLOR_BORDER, COLOR_GOLD, COLOR_GOLD_LIGHT,
    COLOR_WHITE, COLOR_TEXT_MUTED, COLOR_TEXT_PARCHMENT, COLOR_ACCENT_GREEN,
    COLOR_ACCENT_RED, COLOR_ACCENT_BLUE, get_qt_font
)
from app_qt.services.sound_service_qt import get_sound_service_qt


class CreateCaseScreenQt(QWidget):
    """Screen for creating and publishing custom courtroom cases."""

    navigate = Signal(str)
    notify = Signal(str, str)

    def __init__(self, game_state: GameState, case_service: Optional[CaseService] = None, save_service: Optional[SaveService] = None, parent=None):
        super().__init__(parent)
        self.game_state = game_state
        self.case_service = case_service or CaseService()
        self.save_service = save_service or SaveService()
        self.sound_service = get_sound_service_qt()

        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 16, 24, 16)
        main_layout.setSpacing(12)

        # 1. Header Bar
        header_layout = QHBoxLayout()
        btn_back = QPushButton("← BACK")
        btn_back.setFont(get_qt_font(10, bold=True))
        btn_back.setStyleSheet("padding: 7px 16px; background-color: #2b1f14; color: #c9a050; border: 1px solid #5a381e; border-radius: 4px;")
        btn_back.clicked.connect(lambda: self.navigate.emit("case_selection"))
        header_layout.addWidget(btn_back)

        title_lbl = QLabel("AUTHOR NEW INVESTIGATION CASE")
        title_lbl.setFont(get_qt_font(16, bold=True))
        title_lbl.setStyleSheet(f"color: {COLOR_GOLD.name()}; margin-left: 12px;")
        header_layout.addWidget(title_lbl)

        header_layout.addStretch()

        btn_save = QPushButton("SAVE & PUBLISH CASE ➔")
        btn_save.setFont(get_qt_font(11, bold=True))
        btn_save.setStyleSheet(f"padding: 8px 18px; background-color: {COLOR_ACCENT_GREEN.name()}; color: #fff; border: 1px solid #3d8c3d; border-radius: 4px;")
        btn_save.clicked.connect(self._save_case)
        header_layout.addWidget(btn_save)

        main_layout.addLayout(header_layout)

        # 2. Form Scroll Area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background-color: transparent; border: none;")

        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)
        form_layout.setSpacing(14)

        # Section 1: Dossier Particulars
        sec1_lbl = QLabel("1. CASE DOSSIER & PARTICULARS:")
        sec1_lbl.setFont(get_qt_font(11, bold=True))
        sec1_lbl.setStyleSheet(f"color: {COLOR_GOLD.name()};")
        form_layout.addWidget(sec1_lbl)

        row1 = QHBoxLayout()
        row1.setSpacing(10)

        self.txt_title = QLineEdit()
        self.txt_title.setPlaceholderText("Case Title (e.g. The Midnight Heirloom Heist)...")
        self.txt_title.setStyleSheet(self._input_style())
        row1.addWidget(self.txt_title, stretch=3)

        self.txt_type = QLineEdit()
        self.txt_type.setText("Theft Investigation")
        self.txt_type.setPlaceholderText("Investigation Type...")
        self.txt_type.setStyleSheet(self._input_style())
        row1.addWidget(self.txt_type, stretch=2)

        self.combo_diff = QComboBox()
        self.combo_diff.addItems(["EASY", "MEDIUM", "HARD"])
        self.combo_diff.setCurrentText("MEDIUM")
        self.combo_diff.setStyleSheet(f"""
            QComboBox {{
                background-color: #17110e;
                color: #e6d3a3;
                border: 1px solid #3d2b1f;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }}
            QComboBox QAbstractItemView {{
                background-color: #17110e;
                color: #e6d3a3;
                selection-background-color: #5a381e;
            }}
        """)
        row1.addWidget(self.combo_diff, stretch=1)
        form_layout.addLayout(row1)

        # Description
        sec2_lbl = QLabel("2. BACKGROUND NARRATIVE:")
        sec2_lbl.setFont(get_qt_font(11, bold=True))
        sec2_lbl.setStyleSheet(f"color: {COLOR_GOLD.name()};")
        form_layout.addWidget(sec2_lbl)

        self.txt_desc = QTextEdit()
        self.txt_desc.setFixedHeight(75)
        self.txt_desc.setPlaceholderText("Provide the crime scene incident summary, time of discovery, and initial circumstances...")
        self.txt_desc.setStyleSheet(self._input_style())
        form_layout.addWidget(self.txt_desc)

        # Suspects
        sec3_lbl = QLabel("3. PERSONS OF INTEREST & SWORN STATEMENTS:")
        sec3_lbl.setFont(get_qt_font(11, bold=True))
        sec3_lbl.setStyleSheet(f"color: {COLOR_GOLD.name()};")
        form_layout.addWidget(sec3_lbl)

        sus_layout = QHBoxLayout()
        sus_layout.setSpacing(12)

        # Suspect 1
        s1_frame = QFrame()
        s1_frame.setStyleSheet(f"background-color: {COLOR_BG_CARD.name()}; border: 1px solid {COLOR_BORDER.name()}; border-radius: 6px; padding: 10px;")
        s1_layout = QVBoxLayout(s1_frame)
        s1_layout.setSpacing(6)
        s1_title = QLabel("Primary Suspect (Accused):")
        s1_title.setFont(get_qt_font(9, bold=True))
        s1_title.setStyleSheet(f"color: {COLOR_GOLD.name()};")
        s1_layout.addWidget(s1_title)

        self.txt_s1_name = QLineEdit("Lord Reginald")
        self.txt_s1_name.setPlaceholderText("Suspect 1 Name...")
        self.txt_s1_name.setStyleSheet(self._input_style())
        s1_layout.addWidget(self.txt_s1_name)

        self.txt_s1_stmt = QTextEdit("I was in the cellar all evening tasting vintage wines.")
        self.txt_s1_stmt.setFixedHeight(55)
        self.txt_s1_stmt.setPlaceholderText("Suspect 1 Alibi Statement...")
        self.txt_s1_stmt.setStyleSheet(self._input_style())
        s1_layout.addWidget(self.txt_s1_stmt)
        sus_layout.addWidget(s1_frame)

        # Suspect 2
        s2_frame = QFrame()
        s2_frame.setStyleSheet(f"background-color: {COLOR_BG_CARD.name()}; border: 1px solid {COLOR_BORDER.name()}; border-radius: 6px; padding: 10px;")
        s2_layout = QVBoxLayout(s2_frame)
        s2_layout.setSpacing(6)
        s2_title = QLabel("Secondary Suspect (Witness):")
        s2_title.setFont(get_qt_font(9, bold=True))
        s2_title.setStyleSheet(f"color: {COLOR_GOLD.name()};")
        s2_layout.addWidget(s2_title)

        self.txt_s2_name = QLineEdit("Lady Beatrice")
        self.txt_s2_name.setPlaceholderText("Suspect 2 Name...")
        self.txt_s2_name.setStyleSheet(self._input_style())
        s2_layout.addWidget(self.txt_s2_name)

        self.txt_s2_stmt = QTextEdit("I was in the drawing room reading under the gaslight.")
        self.txt_s2_stmt.setFixedHeight(55)
        self.txt_s2_stmt.setPlaceholderText("Suspect 2 Alibi Statement...")
        self.txt_s2_stmt.setStyleSheet(self._input_style())
        s2_layout.addWidget(self.txt_s2_stmt)
        sus_layout.addWidget(s2_frame)

        form_layout.addLayout(sus_layout)

        # Evidence
        sec4_lbl = QLabel("4. CRIME SCENE FORENSIC EVIDENCE:")
        sec4_lbl.setFont(get_qt_font(11, bold=True))
        sec4_lbl.setStyleSheet(f"color: {COLOR_GOLD.name()};")
        form_layout.addWidget(sec4_lbl)

        ev_layout = QHBoxLayout()
        ev_layout.setSpacing(12)

        # Evidence 1
        e1_frame = QFrame()
        e1_frame.setStyleSheet(f"background-color: {COLOR_BG_CARD.name()}; border: 1px solid {COLOR_BORDER.name()}; border-radius: 6px; padding: 10px;")
        e1_layout = QVBoxLayout(e1_frame)
        e1_layout.setSpacing(6)
        e1_title = QLabel("Evidence Item 1:")
        e1_title.setFont(get_qt_font(9, bold=True))
        e1_title.setStyleSheet(f"color: {COLOR_GOLD.name()};")
        e1_layout.addWidget(e1_title)

        self.txt_e1_name = QLineEdit("Stained Glove")
        self.txt_e1_name.setPlaceholderText("Evidence 1 Name...")
        self.txt_e1_name.setStyleSheet(self._input_style())
        e1_layout.addWidget(self.txt_e1_name)

        self.txt_e1_desc = QTextEdit("Silk glove matching Reginald found by the unlocked window.")
        self.txt_e1_desc.setFixedHeight(55)
        self.txt_e1_desc.setPlaceholderText("Forensic Description...")
        self.txt_e1_desc.setStyleSheet(self._input_style())
        e1_layout.addWidget(self.txt_e1_desc)
        ev_layout.addWidget(e1_frame)

        # Evidence 2
        e2_frame = QFrame()
        e2_frame.setStyleSheet(f"background-color: {COLOR_BG_CARD.name()}; border: 1px solid {COLOR_BORDER.name()}; border-radius: 6px; padding: 10px;")
        e2_layout = QVBoxLayout(e2_frame)
        e2_layout.setSpacing(6)
        e2_title = QLabel("Evidence Item 2:")
        e2_title.setFont(get_qt_font(9, bold=True))
        e2_title.setStyleSheet(f"color: {COLOR_GOLD.name()};")
        e2_layout.addWidget(e2_title)

        self.txt_e2_name = QLineEdit("Broken Lock")
        self.txt_e2_name.setPlaceholderText("Evidence 2 Name...")
        self.txt_e2_name.setStyleSheet(self._input_style())
        e2_layout.addWidget(self.txt_e2_name)

        self.txt_e2_desc = QTextEdit("Lock picked cleanly from outside without structural damage.")
        self.txt_e2_desc.setFixedHeight(55)
        self.txt_e2_desc.setPlaceholderText("Forensic Description...")
        self.txt_e2_desc.setStyleSheet(self._input_style())
        e2_layout.addWidget(self.txt_e2_desc)
        ev_layout.addWidget(e2_frame)

        form_layout.addLayout(ev_layout)
        scroll.setWidget(form_container)
        main_layout.addWidget(scroll, stretch=1)

    def _input_style(self) -> str:
        return f"""
            QLineEdit, QTextEdit {{
                background-color: #17110e;
                color: #e6d3a3;
                border: 1px solid #3d2b1f;
                border-radius: 4px;
                padding: 6px 10px;
            }}
            QLineEdit:focus, QTextEdit:focus {{
                border: 1px solid {COLOR_GOLD.name()};
            }}
        """

    def _save_case(self):
        title = self.txt_title.text().strip()
        case_type = self.txt_type.text().strip() or "Custom Investigation"
        diff = self.combo_diff.currentText()
        desc = self.txt_desc.toPlainText().strip()

        s1_name = self.txt_s1_name.text().strip()
        s1_stmt = self.txt_s1_stmt.toPlainText().strip()
        s2_name = self.txt_s2_name.text().strip()
        s2_stmt = self.txt_s2_stmt.toPlainText().strip()

        e1_name = self.txt_e1_name.text().strip()
        e1_desc = self.txt_e1_desc.toPlainText().strip()
        e2_name = self.txt_e2_name.text().strip()
        e2_desc = self.txt_e2_desc.toPlainText().strip()

        if not title:
            self.notify.emit("WARNING", "Please enter a Case Title!")
            return
        if not desc:
            self.notify.emit("WARNING", "Please provide a Case Description!")
            return
        if not s1_name or not s2_name:
            self.notify.emit("WARNING", "Please provide at least two suspects!")
            return
        if not e1_name or not e2_name:
            self.notify.emit("WARNING", "Please provide at least two evidence items!")
            return

        new_id = f"CASE-{uuid.uuid4().hex[:4].upper()}"

        suspects = [
            Suspect(
                id="SUS-001",
                name=s1_name,
                occupation="Custom Role",
                relationship="Associate",
                motive="Custom motive for investigation.",
                alibi=s1_stmt,
                statement=s1_stmt,
                known_facts=["suspect_1_present"],
                contradictions=[],
                avatar_type="partner",
                is_guilty=True
            ),
            Suspect(
                id="SUS-002",
                name=s2_name,
                occupation="Witness Role",
                relationship="Colleague",
                motive="Secondary motive.",
                alibi=s2_stmt,
                statement=s2_stmt,
                known_facts=["suspect_2_present"],
                contradictions=[],
                avatar_type="heir",
                is_guilty=False
            )
        ]

        evidence_list = [
            Evidence(
                id="EVD-001",
                name=e1_name,
                description=e1_desc,
                category="Physical",
                reliability=0.9,
                relevance=0.85,
                collected=False,
                scene_pos=[320, 260, 60, 60],
                icon_type="glass",
                facts_unlocked=["evidence_1_verified"],
                details=e1_desc
            ),
            Evidence(
                id="EVD-002",
                name=e2_name,
                description=e2_desc,
                category="Direct",
                reliability=0.85,
                relevance=0.9,
                collected=False,
                scene_pos=[550, 360, 60, 60],
                icon_type="document",
                facts_unlocked=["evidence_2_verified"],
                details=e2_desc
            )
        ]

        new_case = Case(
            id=new_id,
            title=title,
            type=case_type,
            description=desc,
            difficulty=diff,
            reward=300,
            scene_name="Custom Manor Chamber",
            scene_type="manor",
            solution_suspect_id="SUS-001",
            solution_conclusion="suspect_guilty_beyond_reasonable_doubt",
            solution_summary=f"Accused {s1_name} was proven guilty by forensic connections.",
            suspects=suspects,
            evidence_list=evidence_list,
            initial_facts=["crime_committed", "suspect_1_present"],
            rules=[]
        )

        success = self.case_service.create_case(new_case)
        if success:
            self.sound_service.play("evidence")
            self.notify.emit("SUCCESS", f"Case '{title}' created and published successfully!")
            self.navigate.emit("case_selection")
        else:
            self.notify.emit("ERROR", "Failed to save custom case to disk.")

    def on_enter_screen(self):
        pass

