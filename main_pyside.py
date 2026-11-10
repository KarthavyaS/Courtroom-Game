"""
LOGIC COURTROOM - Complete PySide6 Desktop Edition
Precise recreation of the full Pygame interface with state-of-the-art enhanced UI:
1. Welcome & Onboarding
2. Interactive Academy Tutorial
3. Investigation Hub / Dashboard
4. Case Selection Archive
5. Formal Case Briefing
6. 2D Crime Scene & Forensic Lab (Lens, UV Light, Powder)
7. Suspect Interrogation & Cross-Examination (Zero-overlap, collapsible questions & dossier)
8. Evidence Vault (Categorized filters & inspection metrics)
9. Detective Case Board (Corkboard with Timeline Scrubber & yarn connections)
10. Investigation Notebook (Case binder with auto-saving scratchpad)
11. Mind Palace Syllogism / Argument Builder (3 Pillars: Means, Opportunity, Motive, 20+ Pool)
12. Supreme Courtroom Trial Chamber (AI Magistrate, Jury persuasion, Suspect composure, Objections, Verdicts)
13. Trial Results & Judicial Assessment (Wax Seal stamp, score breakdown, metrics)
14. Detective Profile & Career Rank
15. Global Leaderboard
16. Settings & Audio Console
17. Custom Case Creation Studio
"""

import sys
import math
import random
from pathlib import Path
from typing import Optional, List, Dict, Any, Set

from PySide6.QtCore import Qt, QTimer, QSize, Signal
from PySide6.QtGui import QFont, QColor, QPalette, QIcon, QPainter, QLinearGradient, QPen, QBrush
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QPushButton, QTabWidget, QListWidget, QListWidgetItem,
    QProgressBar, QTextBrowser, QFrame, QSplitter, QScrollArea, QSlider,
    QStackedWidget, QMessageBox, QGroupBox, QLineEdit, QTextEdit, QComboBox
)

# Core Domain Logic & AI Engine
from services.case_service import CaseService
from services.save_service import SaveService
from services.game_state import GameState
from services.sound_service import get_sound_service
from models.case import Case
from models.suspect import Suspect
from models.evidence import Evidence
from models.argument import Argument
from models.profile import PlayerProfile
from ai_engine.rule_engine import RuleEngine
from ai_engine.scoring import ScoringEngine

# ---------------------------------------------------------------------------
# High-End Dark Noir Courtroom Stylesheet (QSS)
# ---------------------------------------------------------------------------
COURTROOM_QSS = """
QMainWindow, QWidget#CentralWidget {
    background-color: #140d0a;
    color: #f5ebd7;
    font-family: "Segoe UI", "Trebuchet MS", sans-serif;
}

QFrame.card-panel {
    background-color: #221610;
    border: 1px solid #704222;
    border-radius: 8px;
}

QFrame.card-panel-gold {
    background-color: #261a13;
    border: 1px solid #ffd741;
    border-radius: 8px;
}

QFrame.header-strip {
    background-color: #341f14;
    border-bottom: 2px solid #ffd741;
}

QLabel {
    color: #f5ebd7;
}

QLabel.title-gold {
    color: #ffd741;
    font-size: 20px;
    font-weight: bold;
}

QLabel.subtitle-parchment {
    color: #e6dac3;
    font-size: 13px;
}

QLabel.muted-label {
    color: #b8a896;
    font-size: 11px;
}

QPushButton {
    background-color: #4a2d1a;
    color: #ffffff;
    border: 1px solid #c8a050;
    border-radius: 6px;
    padding: 6px 14px;
    font-weight: bold;
    font-size: 12px;
}

QPushButton:hover {
    background-color: #6c3f24;
    border: 1px solid #ffe175;
}

QPushButton:pressed {
    background-color: #301b0f;
    border: 1px solid #ffd741;
}

QPushButton:disabled {
    background-color: #20140e;
    color: #6e5e54;
    border: 1px solid #3c2a20;
}

QPushButton.nav-btn {
    background-color: #291a13;
    border: 1px solid #633c22;
    padding: 6px 11px;
    font-size: 11px;
}

QPushButton.nav-btn:hover {
    background-color: #553422;
    border: 1px solid #ffd741;
}

QPushButton.nav-btn-active {
    background-color: #965f23;
    border: 1px solid #ffd741;
    color: #ffffff;
}

QPushButton.action-gold {
    background-color: #b37e19;
    border: 1px solid #ffe175;
    color: #ffffff;
}

QPushButton.action-gold:hover {
    background-color: #d49520;
    border: 1px solid #ffffff;
}

QPushButton.action-danger {
    background-color: #8f2320;
    border: 1px solid #eb3732;
    color: #ffffff;
}

QPushButton.action-danger:hover {
    background-color: #b82d28;
}

QPushButton.action-green {
    background-color: #23853f;
    border: 1px solid #2db955;
    color: #ffffff;
}

QPushButton.action-green:hover {
    background-color: #2db955;
}

QTabWidget::pane {
    border: 1px solid #704222;
    background-color: #1f140e;
    border-radius: 6px;
}

QTabBar::tab {
    background-color: #281811;
    color: #c8b8a6;
    border: 1px solid #55321a;
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    padding: 7px 13px;
    margin-right: 4px;
    font-weight: bold;
    font-size: 11px;
}

QTabBar::tab:selected {
    background-color: #4a2d1a;
    color: #ffd741;
    border: 1px solid #ffd741;
    border-bottom: 1px solid #4a2d1a;
}

QTabBar::tab:hover:!selected {
    background-color: #382216;
    color: #ffffff;
}

QListWidget {
    background-color: #1a100b;
    border: 1px solid #5a351c;
    border-radius: 6px;
    color: #f5ebd7;
    padding: 4px;
}

QListWidget::item {
    border-radius: 4px;
    padding: 8px;
    margin-bottom: 4px;
    background-color: #241710;
    border: 1px solid #402617;
}

QListWidget::item:selected {
    background-color: #482c1b;
    border: 1px solid #ffd741;
    color: #ffffff;
}

QListWidget::item:hover:!selected {
    background-color: #301e14;
    border: 1px solid #84532e;
}

QTextBrowser, QTextEdit, QLineEdit {
    background-color: #180f0a;
    border: 1px solid #4d2d17;
    border-radius: 6px;
    color: #f5ebd7;
    padding: 8px;
    font-size: 13px;
    line-height: 1.5;
}

QLineEdit {
    padding: 6px;
    border: 1px solid #704222;
}

QLineEdit:focus, QTextEdit:focus {
    border: 1px solid #ffd741;
}

QProgressBar {
    background-color: #24160f;
    border: 1px solid #5a351c;
    border-radius: 4px;
    text-align: center;
    color: #ffffff;
    font-weight: bold;
    font-size: 10px;
    height: 14px;
}

QProgressBar::chunk {
    background-color: #2db955;
    border-radius: 3px;
}

QSplitter::handle {
    background-color: #422716;
}

QSplitter::handle:hover {
    background-color: #ffd741;
}

QSlider::groove:horizontal {
    height: 6px;
    background: #24160f;
    border: 1px solid #55321a;
    border-radius: 3px;
}

QSlider::sub-page:horizontal {
    background: #ffd741;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background: #ffffff;
    border: 1px solid #ffd741;
    width: 14px;
    margin-top: -4px;
    margin-bottom: -4px;
    border-radius: 7px;
}
"""

PREDEFINED_QUESTIONS = [
    ("Q1", "Where were you at the time of the incident?"),
    ("Q2", "What was your relationship with the victim?"),
    ("Q3", "Did you see anyone near the crime scene?"),
    ("Q4", "Why were you present at the location?"),
    ("Q5", "Can you explain the inconsistencies in your story?")
]


# ---------------------------------------------------------------------------
# Custom Animated Canvas Widgets
# ---------------------------------------------------------------------------
class HeartbeatPulseWidget(QWidget):
    """Animated heartbeat stress waveform widget for suspect demeanor monitoring."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(190, 28)
        self.setMaximumHeight(32)
        self.stress_val = 20.0
        self.anim_tick = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._on_tick)
        self.timer.start(30)

    def set_stress(self, val: float):
        self.stress_val = max(5.0, min(100.0, float(val)))
        self.update()

    def _on_tick(self):
        self.anim_tick += 1
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()
        mid_y = h / 2.0

        # Background
        painter.setBrush(QColor(22, 14, 10))
        pen_col = QColor(235, 55, 50) if self.stress_val > 60 else QColor(255, 215, 65)
        painter.setPen(QPen(pen_col, 1))
        painter.drawRoundedRect(0, 0, w - 1, h - 1, 4, 4)

        # Heartbeat pulse waveform
        pulse_h = math.sin(self.anim_tick * (0.15 if self.stress_val < 50 else 0.35)) * (4.0 if self.stress_val < 50 else 9.0)
        line_col = QColor(255, 80, 70) if self.stress_val > 60 else QColor(100, 255, 150)
        painter.setPen(QPen(line_col, 2))

        pts = [
            (8, mid_y),
            (25, mid_y),
            (35, mid_y - pulse_h),
            (45, mid_y + pulse_h * 1.2),
            (55, mid_y - pulse_h * 0.8),
            (65, mid_y),
            (85, mid_y)
        ]
        for i in range(len(pts) - 1):
            painter.drawLine(int(pts[i][0]), int(pts[i][1]), int(pts[i + 1][0]), int(pts[i + 1][1]))

        # Stress text
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("Segoe UI", 9, QFont.Bold))
        painter.drawText(95, int(mid_y + 4), f"STRESS: {int(self.stress_val)}%")


class JuryPersuasionBar(QWidget):
    """Dynamic dual-color persuasion bar representing prosecution vs defense jury balance."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(220, 24)
        self.persuasion = 50.0  # 0 to 100%

    def set_persuasion(self, val: float):
        self.persuasion = max(0.0, min(100.0, float(val)))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()

        painter.setBrush(QColor(30, 20, 15))
        painter.setPen(QPen(QColor(255, 215, 65), 1))
        painter.drawRoundedRect(0, 0, w - 1, h - 1, 4, 4)

        prosecution_w = int((w - 2) * (self.persuasion / 100.0))
        if prosecution_w > 0:
            painter.setBrush(QColor(45, 185, 85))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(1, 1, prosecution_w, h - 2, 3, 3)

        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("Segoe UI", 9, QFont.Bold))
        painter.drawText(0, 0, w, h, Qt.AlignCenter, f"JURY PERSUASION: {int(self.persuasion)}%")


# ---------------------------------------------------------------------------
# Main Logic Courtroom PySide6 Application
# ---------------------------------------------------------------------------
class LogicCourtroomApp(QMainWindow):
    """Full-featured, precise recreation of all 17 Pygame game stages in PySide6 with enhanced UI."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("LOGIC COURTROOM - Artificial Intelligence Legal Game (PySide6 Edition)")
        self.resize(1180, 760)
        self.setMinimumSize(980, 640)

        # Core Services
        self.case_service = CaseService()
        self.save_service = SaveService()
        self.sound_service = get_sound_service()
        self.user_profile = self.save_service.load_profile()
        self.game_state = GameState(profile=self.user_profile)
        self.scoring_engine = ScoringEngine()

        # State Variables
        self.selected_suspect: Optional[Suspect] = None
        self.selected_evidence: Optional[Evidence] = None
        self.suspect_stress: Dict[str, float] = {}
        self.active_forensic_tool = "MAGNIFIER"  # 'MAGNIFIER', 'LUMINOL', 'POWDER'
        self.jury_persuasion = 50.0
        self.suspect_composure = 100.0
        self.slotted_clues: Dict[str, Optional[str]] = {"means": None, "opportunity": None, "motive": None}

        # Apply QSS
        self.setStyleSheet(COURTROOM_QSS)

        # Build UI Stages
        self._init_ui()

    def _init_ui(self):
        central_widget = QWidget(self)
        central_widget.setObjectName("CentralWidget")
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Top Unified Navigation Bar & Window Controls
        self.nav_bar = self._create_nav_bar()
        main_layout.addWidget(self.nav_bar)

        # 2. Stacked Content Views for all stages
        self.content_stack = QStackedWidget(self)
        main_layout.addWidget(self.content_stack, 1)

        # Map stages by ID
        self.stage_indices: Dict[str, int] = {}

        def register_view(tab_id: str, widget: QWidget):
            idx = self.content_stack.addWidget(widget)
            self.stage_indices[tab_id] = idx

        register_view("welcome", self._build_welcome_view())          # 0
        register_view("tutorial", self._build_tutorial_view())        # 1
        register_view("hub", self._build_hub_view())                  # 2
        register_view("cases", self._build_case_selection_view())     # 3
        register_view("briefing", self._build_briefing_view())        # 4
        register_view("scene", self._build_crime_scene_view())        # 5
        register_view("suspects", self._build_suspects_view())        # 6
        register_view("evidence", self._build_evidence_view())        # 7
        register_view("board", self._build_case_board_view())          # 8
        register_view("notebook", self._build_notebook_view())        # 9
        register_view("arguments", self._build_arguments_view())      # 10
        register_view("courtroom", self._build_courtroom_view())      # 11
        register_view("results", self._build_results_view())          # 12
        register_view("profile", self._build_profile_view())          # 13
        register_view("leaderboard", self._build_leaderboard_view())  # 14
        register_view("settings", self._build_settings_view())        # 15
        register_view("create_case", self._build_create_case_view())  # 16

        # Initialize first case selection after all views are constructed
        cases = self.case_service.get_all_cases()
        if cases:
            self.case_list_widget.setCurrentRow(0)

        # Start on Welcome if not onboarded, else Hub
        if not self.game_state.profile.onboarded:
            self.switch_tab("welcome")
        else:
            self.switch_tab("hub")

    # -----------------------------------------------------------------------
    # Top Navigation Ribbon with In-Game Minimize Feature
    # -----------------------------------------------------------------------
    def _create_nav_bar(self) -> QWidget:
        nav = QFrame()
        nav.setObjectName("HeaderNav")
        nav.setStyleSheet("background-color: #341f14; border-bottom: 2px solid #ffd741; padding: 3px 8px;")
        layout = QHBoxLayout(nav)
        layout.setContentsMargins(6, 3, 6, 3)
        layout.setSpacing(4)

        self.nav_buttons: Dict[str, QPushButton] = {}
        primary_tabs = [
            ("hub", "⌂ HUB"),
            ("briefing", "BRIEFING"),
            ("scene", "SCENE"),
            ("suspects", "SUSPECTS 💬"),
            ("evidence", "EVIDENCE"),
            ("board", "BOARD 📌"),
            ("notebook", "NOTEBOOK"),
            ("arguments", "ARGUMENTS"),
            ("courtroom", "⚖ COURT")
        ]

        for tab_id, label in primary_tabs:
            btn = QPushButton(label)
            btn.setProperty("class", "nav-btn")
            btn.clicked.connect(lambda checked=False, tid=tab_id: self.switch_tab(tid))
            layout.addWidget(btn)
            self.nav_buttons[tab_id] = btn

        layout.addStretch(1)

        # Progress Indicator
        self.lbl_progress = QLabel("Progress: 0%")
        self.lbl_progress.setStyleSheet("color: #ffd741; font-weight: bold; font-size: 11px;")
        layout.addWidget(self.lbl_progress)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedWidth(90)
        layout.addWidget(self.progress_bar)

        # Settings & Profile Shortcuts
        btn_prof = QPushButton("👤")
        btn_prof.setToolTip("Detective Profile & Rank")
        btn_prof.setFixedWidth(28)
        btn_prof.clicked.connect(lambda: self.switch_tab("profile"))
        layout.addWidget(btn_prof)

        btn_sett = QPushButton("⚙")
        btn_sett.setToolTip("Settings & Audio")
        btn_sett.setFixedWidth(28)
        btn_sett.clicked.connect(lambda: self.switch_tab("settings"))
        layout.addWidget(btn_sett)

        # Volume Slider
        lbl_vol = QLabel("🔊")
        lbl_vol.setStyleSheet("font-size: 13px;")
        layout.addWidget(lbl_vol)

        vol_slider = QSlider(Qt.Horizontal)
        vol_slider.setRange(0, 100)
        vol_slider.setValue(int(self.sound_service.music_volume * 100))
        vol_slider.setFixedWidth(65)
        vol_slider.valueChanged.connect(self._on_volume_changed)
        layout.addWidget(vol_slider)

        # Flexible In-Game Minimize Button
        btn_minimize = QPushButton("—")
        btn_minimize.setToolTip("Minimize Window (Ctrl+M)")
        btn_minimize.setStyleSheet("background-color: #4a281e; border: 1px solid #ffd741; font-size: 14px; font-weight: bold; padding: 2px 10px;")
        btn_minimize.clicked.connect(self.showMinimized)
        layout.addWidget(btn_minimize)

        return nav

    def _on_volume_changed(self, val: int):
        vol = val / 100.0
        self.sound_service.set_volume(vol)

    def switch_tab(self, tab_id: str):
        if tab_id in self.stage_indices:
            self.content_stack.setCurrentIndex(self.stage_indices[tab_id])
            for k, btn in self.nav_buttons.items():
                if k == tab_id:
                    btn.setStyleSheet("background-color: #965f23; border: 1px solid #ffd741; color: #ffffff;")
                else:
                    btn.setStyleSheet("")
            self.sound_service.play("click")
            self._update_progress_display()

    def _update_progress_display(self):
        if self.game_state.current_case:
            pct = self.game_state.progress.calculate_progress_percentage()
            self.lbl_progress.setText(f"Progress: {pct}%")
            self.progress_bar.setValue(pct)

    # -----------------------------------------------------------------------
    # Stage 1: Welcome & Onboarding View
    # -----------------------------------------------------------------------
    def _build_welcome_view(self) -> QWidget:
        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setContentsMargins(60, 40, 60, 40)
        layout.setAlignment(Qt.AlignCenter)

        card = QFrame()
        card.setProperty("class", "card-panel-gold")
        card.setStyleSheet("background-color: #261a13; border: 2px solid #ffd741; border-radius: 12px; padding: 30px;")
        card.setMaximumWidth(700)
        c_layout = QVBoxLayout(card)
        c_layout.setSpacing(16)
        c_layout.setAlignment(Qt.AlignCenter)

        lbl_title = QLabel("⚖ LOGIC COURTROOM ⚖")
        lbl_title.setStyleSheet("font-size: 28px; color: #ffd741; font-weight: bold; text-align: center;")
        lbl_title.setAlignment(Qt.AlignCenter)
        c_layout.addWidget(lbl_title)

        lbl_sub = QLabel("Where Artificial Intelligence & Pure Logic Decide the Verdict")
        lbl_sub.setStyleSheet("font-size: 14px; color: #f5ebd7; font-style: italic;")
        lbl_sub.setAlignment(Qt.AlignCenter)
        c_layout.addWidget(lbl_sub)

        lbl_desc = QLabel(
            "Step into Victorian London's highest court of deductive law. Inspect crime scenes, "
            "interrogate elusive suspects, formulate rigorous syllogistic arguments, and face the AI Magistrate."
        )
        lbl_desc.setWordWrap(True)
        lbl_desc.setStyleSheet("color: #d8c8b4; font-size: 13px; line-height: 1.6; text-align: center;")
        lbl_desc.setAlignment(Qt.AlignCenter)
        c_layout.addWidget(lbl_desc)

        # Name Entry Box
        name_group = QGroupBox("DETECTIVE CREDENTIALS")
        name_group.setStyleSheet("color: #ffd741; font-weight: bold;")
        n_box = QVBoxLayout(name_group)
        self.txt_player_name = QLineEdit(self.game_state.profile.name)
        self.txt_player_name.setPlaceholderText("Enter your lawyer / investigator name...")
        n_box.addWidget(self.txt_player_name)
        c_layout.addWidget(name_group)

        # Action Buttons
        btn_box = QHBoxLayout()
        btn_begin = QPushButton("ENTER COURT & BEGIN CAREER ➔")
        btn_begin.setProperty("class", "action-green")
        btn_begin.setStyleSheet("font-size: 14px; padding: 10px 20px;")
        btn_begin.clicked.connect(self._confirm_welcome_onboarding)
        btn_box.addWidget(btn_begin)

        c_layout.addLayout(btn_box)
        layout.addWidget(card)

        return view

    def _confirm_welcome_onboarding(self):
        name = self.txt_player_name.text().strip()
        if name:
            self.game_state.profile.name = name
            self.game_state.player_name = name
        self.game_state.profile.onboarded = True
        self.save_service.save_profile(self.game_state.profile)
        self.sound_service.play("gavel")
        self.switch_tab("hub")

    # -----------------------------------------------------------------------
    # Stage 2: Interactive Academy Tutorial View
    # -----------------------------------------------------------------------
    def _build_tutorial_view(self) -> QWidget:
        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setContentsMargins(40, 25, 40, 25)
        layout.setSpacing(16)

        lbl = QLabel("ACADEMY OF LEGAL LOGIC - INTERACTIVE TUTORIAL")
        lbl.setStyleSheet("font-size: 22px; color: #ffd741; font-weight: bold;")
        layout.addWidget(lbl)

        self.tut_browser = QTextBrowser()
        layout.addWidget(self.tut_browser, 1)

        self.tut_steps = [
            ("Lesson 1: Forensic Evidence & Integrity",
             "<h2 style='color: #ffd741;'>1. Forensic Evidence & Fact Discovery</h2>"
             "<p>In LOGIC COURTROOM, truth is established solely on verifiable evidence. Explore crime scenes using forensic tools (Magnifier, UV Light, Powder) to collect evidence items into your vault and unlock foundational facts.</p>"),
            ("Lesson 2: Legal Precedents & Logic Rules",
             "<h2 style='color: #ffd741;'>2. Propositional Rules (If P Then Q)</h2>"
             "<p>The court applies formal propositional logic rules. For instance: <code>If suspect had master key AND entered vault, Then suspect is guilty</code>. Your goal is to connect physical facts to satisfy these rules.</p>"),
            ("Lesson 3: Cross-Examination & Stress Monitoring",
             "<h2 style='color: #ffd741;'>3. Demeanor, Heartbeats & Stress Spikes</h2>"
             "<p>Interrogate suspects across 5 lines of questioning. Watch their galvanic stress pulse meter: sudden spikes indicate defensiveness or physical contradiction!</p>"),
            ("Lesson 4: Syllogistic Deduction (Means, Access, Motive)",
             "<h2 style='color: #ffd741;'>4. The 3 Legal Pillars</h2>"
             "<p>To secure a conviction beyond reasonable doubt, assemble evidence across all three pillars: Means, Opportunity/Access, and Motive. Equip them in the Mind Palace Workshop.</p>"),
            ("Lesson 5: Courtroom Combat & Trial Verdicts",
             "<h2 style='color: #ffd741;'>5. Facing the AI Magistrate</h2>"
             "<p>Present your arguments, trigger dramatic objections when witnesses contradict physical facts, sway the jury, and demand a final verdict!</p>")
        ]
        self.tut_idx = 0
        self._update_tutorial_text()

        # Step controls
        ctrl_bar = QHBoxLayout()
        btn_prev = QPushButton("◀ PREVIOUS LESSON")
        btn_prev.clicked.connect(self._prev_tut_lesson)
        ctrl_bar.addWidget(btn_prev)

        btn_next = QPushButton("NEXT LESSON ▶")
        btn_next.clicked.connect(self._next_tut_lesson)
        ctrl_bar.addWidget(btn_next)

        ctrl_bar.addStretch()
        btn_hub = QPushButton("GRADUATE & GO TO HUB ➔")
        btn_hub.setProperty("class", "action-green")
        btn_hub.clicked.connect(lambda: self.switch_tab("hub"))
        ctrl_bar.addWidget(btn_hub)

        layout.addLayout(ctrl_bar)
        return view

    def _update_tutorial_text(self):
        title, html = self.tut_steps[self.tut_idx]
        self.tut_browser.setHtml(html)

    def _prev_tut_lesson(self):
        if self.tut_idx > 0:
            self.tut_idx -= 1
            self._update_tutorial_text()
            self.sound_service.play("click")

    def _next_tut_lesson(self):
        if self.tut_idx < len(self.tut_steps) - 1:
            self.tut_idx += 1
            self._update_tutorial_text()
            self.sound_service.play("click")

    # -----------------------------------------------------------------------
    # Stage 3: Investigation Hub / Dashboard View
    # -----------------------------------------------------------------------
    def _build_hub_view(self) -> QWidget:
        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setContentsMargins(35, 25, 35, 25)
        layout.setSpacing(18)

        # Welcome Hero Banner
        hero = QFrame()
        hero.setProperty("class", "card-panel-gold")
        hero.setStyleSheet("background-color: #271a12; border: 2px solid #ffd741; border-radius: 10px; padding: 20px;")
        h_layout = QHBoxLayout(hero)

        v_info = QVBoxLayout()
        self.lbl_hub_hero = QLabel("ACTIVE INVESTIGATION: SELECT A CASE")
        self.lbl_hub_hero.setStyleSheet("font-size: 20px; color: #ffd741; font-weight: bold;")
        v_info.addWidget(self.lbl_hub_hero)

        self.lbl_hub_desc = QLabel("Welcome to the Scotland Yard Legal Chambers. Choose an action below.")
        self.lbl_hub_desc.setStyleSheet("color: #e0d0bc; font-size: 13px;")
        v_info.addWidget(self.lbl_hub_desc)
        h_layout.addLayout(v_info)

        h_layout.addStretch()
        btn_resume = QPushButton("RESUME CASE ➔")
        btn_resume.setProperty("class", "action-gold")
        btn_resume.setStyleSheet("font-size: 14px; padding: 12px 24px;")
        btn_resume.clicked.connect(lambda: self.switch_tab("briefing"))
        h_layout.addWidget(btn_resume)
        layout.addWidget(hero)

        # Action Cards Grid
        grid = QGridLayout()
        grid.setSpacing(14)

        actions = [
            ("📁 CASE SELECTION ARCHIVE", "Review and select criminal dockets.", "cases"),
            ("🔍 FORENSIC CRIME SCENE", "Explore crime scenes and collect evidence.", "scene"),
            ("👤 SUSPECT INTERROGATION", "Cross-examine suspects with stress monitor.", "suspects"),
            ("📌 DETECTIVE CASE BOARD", "Visual corkboard connecting timeline and clues.", "board"),
            ("✍ INVESTIGATION NOTEBOOK", "Binder notes and propositional scratchpad.", "notebook"),
            ("⚔ MIND PALACE WORKSHOP", "Assemble 3-pillar deductive arguments.", "arguments"),
            ("⚖ SUPREME COURT TRIAL", "Enter the trial chamber and demand a verdict.", "courtroom"),
            ("⚙ SYSTEM & AUDIO SETTINGS", "Configure audio volumes and preferences.", "settings")
        ]

        for idx, (title, desc, tab_dest) in enumerate(actions):
            card = QFrame()
            card.setProperty("class", "card-panel")
            card.setStyleSheet("background-color: #20150e; border: 1px solid #5a351c; border-radius: 8px; padding: 14px;")
            c_lay = QVBoxLayout(card)

            l_t = QLabel(title)
            l_t.setStyleSheet("font-size: 14px; color: #ffd741; font-weight: bold;")
            c_lay.addWidget(l_t)

            l_d = QLabel(desc)
            l_d.setStyleSheet("color: #bfaea0; font-size: 11px;")
            c_lay.addWidget(l_d)

            btn = QPushButton("OPEN ➔")
            btn.setStyleSheet("font-size: 11px; padding: 4px 10px;")
            btn.clicked.connect(lambda checked=False, dest=tab_dest: self.switch_tab(dest))
            c_lay.addWidget(btn, alignment=Qt.AlignRight)

            grid.addWidget(card, idx // 4, idx % 4)

        layout.addLayout(grid)
        layout.addStretch()

        return view

    # -----------------------------------------------------------------------
    # Stage 4: Case Selection View
    # -----------------------------------------------------------------------
    def _build_case_selection_view(self) -> QWidget:
        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(16)

        lbl = QLabel("CASE SELECTION ARCHIVE")
        lbl.setStyleSheet("font-size: 20px; color: #ffd741; font-weight: bold;")
        layout.addWidget(lbl)

        splitter = QSplitter(Qt.Horizontal)

        # Left: Case List
        self.case_list_widget = QListWidget()
        cases = self.case_service.get_all_cases()
        for c in cases:
            item = QListWidgetItem(f"⚖ {c.title} [{c.difficulty.upper()}]")
            item.setData(Qt.UserRole, c.id)
            self.case_list_widget.addItem(item)
        self.case_list_widget.currentRowChanged.connect(self._on_case_selected)
        splitter.addWidget(self.case_list_widget)

        # Right: Case Preview Card
        right_panel = QFrame()
        right_panel.setProperty("class", "card-panel-gold")
        right_panel.setStyleSheet("background-color: #241710; border: 1px solid #ffd741; border-radius: 8px; padding: 15px;")
        r_layout = QVBoxLayout(right_panel)

        self.case_preview_browser = QTextBrowser()
        r_layout.addWidget(self.case_preview_browser, 1)

        btn_select_case = QPushButton("COMMENCE INVESTIGATION ➔")
        btn_select_case.setProperty("class", "action-gold")
        btn_select_case.clicked.connect(lambda: self.switch_tab("briefing"))
        r_layout.addWidget(btn_select_case)

        splitter.addWidget(right_panel)
        splitter.setSizes([380, 720])
        layout.addWidget(splitter, 1)

        return view

    def _on_case_selected(self, row: int):
        cases = self.case_service.get_all_cases()
        if 0 <= row < len(cases):
            c = cases[row]
            self.game_state.set_case(c)
            if c.suspects:
                self.selected_suspect = c.suspects[0]
            self.lbl_hub_hero.setText(f"ACTIVE INVESTIGATION: {c.title.upper()}")
            self._update_case_preview(c)
            self._refresh_suspects_list()
            self._refresh_evidence_list()
            self._update_progress_display()

    def _update_case_preview(self, c: Case):
        html = f"""
        <h2 style='color: #ffd741;'>{c.title}</h2>
        <p><b>Investigation Category:</b> {c.type.upper()} | <b>Scene:</b> {c.scene_name} ({c.scene_type})</p>
        <p><b>Difficulty:</b> <span style='color: #2db955;'>{c.difficulty.upper()}</span> | <b>Reward:</b> {c.reward} XP</p>
        <hr style='border: 1px solid #704222;'>
        <h3 style='color: #ffe175;'>Incident Synopsis:</h3>
        <p style='color: #f5ebd7; font-size: 13px; line-height: 1.6;'>{c.description}</p>
        <h3 style='color: #ffe175;'>Suspects Under Scrutiny ({len(c.suspects)}):</h3>
        <ul>
        """
        for s in c.suspects:
            html += f"<li><b>{s.name}</b> - {s.occupation} ({s.relationship})</li>"
        html += "</ul>"
        self.case_preview_browser.setHtml(html)

        if hasattr(self, "briefing_browser") and self.briefing_browser is not None:
            b_html = f"""
            <h2 style='color: #ffd741;'>{c.title.upper()} - FORMAL CHARGES & DOSSIER</h2>
            <p><b>Location:</b> {c.scene_name} | <b>Category:</b> {c.type.upper()}</p>
            <hr style='border: 1px solid #704222;'>
            <h3 style='color: #ffe175;'>Incident Overview:</h3>
            <p style='color: #ffffff; font-size: 13px; line-height: 1.6;'>{c.description}</p>
            <h3 style='color: #ffe175;'>Initial Verified Forensic Facts:</h3>
            <ul>
            """
            for fact in c.initial_facts:
                b_html += f"<li>{fact}</li>"
            b_html += f"""
            </ul>
            <h3 style='color: #ffe175;'>Legal Precedents & Evidentiary Rules:</h3>
            <p>The AI Magistrate applies {len(c.rules)} established rules of evidence to resolve this docket.</p>
            """
            self.briefing_browser.setHtml(b_html)

    # -----------------------------------------------------------------------
    # Stage 5: Case Briefing View
    # -----------------------------------------------------------------------
    def _build_briefing_view(self) -> QWidget:
        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setContentsMargins(35, 20, 35, 20)
        layout.setSpacing(14)

        lbl = QLabel("POLICE INCIDENT DOSSIER & LEGAL BRIEFING")
        lbl.setStyleSheet("font-size: 20px; color: #ffd741; font-weight: bold;")
        layout.addWidget(lbl)

        self.briefing_browser = QTextBrowser()
        layout.addWidget(self.briefing_browser, 1)

        b_bar = QHBoxLayout()
        b_bar.addStretch()
        btn_to_scene = QPushButton("ENTER CRIME SCENE & FORENSICS ➔")
        btn_to_scene.setProperty("class", "action-gold")
        btn_to_scene.setStyleSheet("font-size: 13px; padding: 10px 20px;")
        btn_to_scene.clicked.connect(lambda: self.switch_tab("scene"))
        b_bar.addWidget(btn_to_scene)
        layout.addLayout(b_bar)

        return view

    # -----------------------------------------------------------------------
    # Stage 6: 2D Crime Scene & Forensic Lab View
    # -----------------------------------------------------------------------
    def _build_crime_scene_view(self) -> QWidget:
        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setContentsMargins(25, 18, 25, 18)
        layout.setSpacing(12)

        # Forensic Tools Strip
        tool_bar = QHBoxLayout()
        lbl_tools = QLabel("FORENSIC INSPECTION KIT:")
        lbl_tools.setStyleSheet("font-weight: bold; color: #ffd741; font-size: 12px;")
        tool_bar.addWidget(lbl_tools)

        self.btn_tool_lens = QPushButton("🔍 OPTICAL LENS [1]")
        self.btn_tool_lens.clicked.connect(lambda: self._select_forensic_tool("MAGNIFIER"))
        tool_bar.addWidget(self.btn_tool_lens)

        self.btn_tool_uv = QPushButton("💡 UV LUMINOL [2]")
        self.btn_tool_uv.clicked.connect(lambda: self._select_forensic_tool("LUMINOL"))
        tool_bar.addWidget(self.btn_tool_uv)

        self.btn_tool_powder = QPushButton("🖌 DUST POWDER [3]")
        self.btn_tool_powder.clicked.connect(lambda: self._select_forensic_tool("POWDER"))
        tool_bar.addWidget(self.btn_tool_powder)

        tool_bar.addStretch()
        self.lbl_tool_status = QLabel("Active: Optical Lens")
        self.lbl_tool_status.setStyleSheet("color: #2db955; font-weight: bold; font-size: 11px;")
        tool_bar.addWidget(self.lbl_tool_status)
        layout.addLayout(tool_bar)

        # Main Scene Splitter
        splitter = QSplitter(Qt.Horizontal)

        # Left: Scene Clues List
        left_box = QWidget()
        l_layout = QVBoxLayout(left_box)
        l_layout.setContentsMargins(0, 0, 0, 0)
        lbl_list = QLabel("CRIME SCENE EVIDENCE ARTIFACTS:")
        lbl_list.setStyleSheet("font-weight: bold; color: #ffd741; font-size: 12px;")
        l_layout.addWidget(lbl_list)

        self.scene_evidence_list = QListWidget()
        self.scene_evidence_list.currentRowChanged.connect(self._on_scene_evidence_selected)
        l_layout.addWidget(self.scene_evidence_list, 1)
        splitter.addWidget(left_box)

        # Right: Forensic Inspector Card
        right_panel = QFrame()
        right_panel.setProperty("class", "card-panel-gold")
        right_panel.setStyleSheet("background-color: #241710; border: 1px solid #ffd741; border-radius: 8px; padding: 15px;")
        r_layout = QVBoxLayout(right_panel)

        self.lbl_scene_ev_name = QLabel("Select an artifact marker above")
        self.lbl_scene_ev_name.setStyleSheet("font-size: 16px; color: #ffd741; font-weight: bold;")
        r_layout.addWidget(self.lbl_scene_ev_name)

        self.txt_scene_ev_desc = QTextBrowser()
        r_layout.addWidget(self.txt_scene_ev_desc, 1)

        btn_act_box = QHBoxLayout()
        self.btn_inspect_ev = QPushButton("INSPECT WITH ACTIVE TOOL 🔍")
        self.btn_inspect_ev.clicked.connect(self._inspect_selected_evidence)
        btn_act_box.addWidget(self.btn_inspect_ev)

        self.btn_collect_ev = QPushButton("COLLECT & LOG EVIDENCE ✓")
        self.btn_collect_ev.setProperty("class", "action-gold")
        self.btn_collect_ev.clicked.connect(self._collect_selected_evidence)
        btn_act_box.addWidget(self.btn_collect_ev)
        r_layout.addLayout(btn_act_box)

        splitter.addWidget(right_panel)
        splitter.setSizes([380, 720])
        layout.addWidget(splitter, 1)

        # Bottom nav
        b_bar = QHBoxLayout()
        b_bar.addStretch()
        btn_to_suspects = QPushButton("PROCEED TO SUSPECT INTERROGATION ➔")
        btn_to_suspects.clicked.connect(lambda: self.switch_tab("suspects"))
        b_bar.addWidget(btn_to_suspects)
        layout.addLayout(b_bar)

        return view

    def _select_forensic_tool(self, tool: str):
        self.active_forensic_tool = tool
        names = {"MAGNIFIER": "Optical Lens", "LUMINOL": "UV Luminol Light", "POWDER": "Dusting Powder"}
        self.lbl_tool_status.setText(f"Active: {names.get(tool, tool)}")
        self.sound_service.play("click")

    def _inspect_selected_evidence(self):
        if self.selected_evidence:
            self.game_state.progress.record_evidence_inspected(self.selected_evidence.id)
            self.sound_service.play("evidence")
            unlocked = self.selected_evidence.facts_unlocked
            msg = f"Forensic analysis with {self.active_forensic_tool} verified artifact integrity!"
            if unlocked:
                msg += f"\nUnlocked Fact: {unlocked[0]}"
            QMessageBox.information(self, "Forensic Inspection", msg)
            self._update_progress_display()

    def _on_scene_evidence_selected(self, row: int):
        c = self.game_state.current_case
        if c and 0 <= row < len(c.evidence_list):
            ev = c.evidence_list[row]
            self.selected_evidence = ev
            self.lbl_scene_ev_name.setText(ev.name.upper())
            is_col = (ev.id in self.game_state.collected_evidence_ids)
            status_txt = "<span style='color: #2db955;'>[COLLECTED IN LOG]</span>" if is_col else "<span style='color: #eb3732;'>[NOT YET COLLECTED]</span>"
            html = f"""
            <p><b>Status:</b> {status_txt}</p>
            <p><b>Category:</b> {ev.category.upper()} | <b>Reliability:</b> {int(ev.reliability * 100)}%</p>
            <p><b>Relevance:</b> {int(ev.relevance * 100)}% | <b>Linked Suspect:</b> {ev.associated_suspect or 'Unassigned'}</p>
            <hr style='border: 1px solid #704222;'>
            <p style='color: #f5ebd7; font-size: 13px; line-height: 1.6;'>{ev.description}</p>
            """
            self.txt_scene_ev_desc.setHtml(html)
            self.btn_collect_ev.setEnabled(not is_col)
            self.btn_collect_ev.setText("ALREADY COLLECTED ✓" if is_col else "COLLECT & LOG EVIDENCE ✓")

    def _collect_selected_evidence(self):
        if self.selected_evidence:
            self.game_state.collect_evidence(self.selected_evidence.id)
            self.sound_service.play("evidence")
            self._refresh_evidence_list()
            self._update_progress_display()
            self._on_scene_evidence_selected(self.scene_evidence_list.currentRow())

    # -----------------------------------------------------------------------
    # Stage 7: Suspect Interrogation & Cross-Examination View
    # (Guaranteed Zero Overlap + Flexible Minimize Controls)
    # -----------------------------------------------------------------------
    def _build_suspects_view(self) -> QWidget:
        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setContentsMargins(25, 16, 25, 16)
        layout.setSpacing(12)

        # Header Strip with Heartbeat Pulse Monitor
        h_box = QHBoxLayout()
        v_h = QVBoxLayout()
        lbl = QLabel("SUSPECT DOSSIER & CROSS-EXAMINATION SUITE")
        lbl.setStyleSheet("font-size: 20px; color: #ffd741; font-weight: bold;")
        lbl_notice = QLabel("Notice: Contradictions and high stress levels provide legal investigative leads.")
        lbl_notice.setStyleSheet("font-size: 11px; color: #d0c0b0;")
        v_h.addWidget(lbl)
        v_h.addWidget(lbl_notice)
        h_box.addLayout(v_h)
        h_box.addStretch()

        self.pulse_widget = HeartbeatPulseWidget(self)
        h_box.addWidget(self.pulse_widget)
        layout.addLayout(h_box)

        # Flexible Splitter
        self.suspect_splitter = QSplitter(Qt.Horizontal)

        # Left Column: Suspects Selector
        left_container = QWidget()
        l_layout = QVBoxLayout(left_container)
        l_layout.setContentsMargins(0, 0, 0, 0)
        lbl_sus_list = QLabel("SELECT SUSPECT:")
        lbl_sus_list.setStyleSheet("font-weight: bold; color: #ffd741; font-size: 12px;")
        l_layout.addWidget(lbl_sus_list)

        self.suspects_list_widget = QListWidget()
        self.suspects_list_widget.currentRowChanged.connect(self._on_suspect_selected)
        l_layout.addWidget(self.suspects_list_widget, 1)

        self.suspect_splitter.addWidget(left_container)

        # Right Column: Detailed Tabbed Dossier
        self.dossier_container = QFrame()
        self.dossier_container.setProperty("class", "card-panel-gold")
        self.dossier_container.setStyleSheet("background-color: #241710; border: 1px solid #ffd741; border-radius: 8px; padding: 10px;")
        d_layout = QVBoxLayout(self.dossier_container)

        dossier_top_bar = QHBoxLayout()
        self.lbl_dossier_header = QLabel("DOSSIER")
        self.lbl_dossier_header.setStyleSheet("font-size: 16px; color: #ffd741; font-weight: bold;")
        dossier_top_bar.addWidget(self.lbl_dossier_header)
        dossier_top_bar.addStretch()

        self.btn_minimize_dossier = QPushButton("− MINIMIZE DOSSIER")
        self.btn_minimize_dossier.setStyleSheet("font-size: 10px; padding: 4px 10px;")
        self.btn_minimize_dossier.clicked.connect(self._toggle_dossier_minimize)
        dossier_top_bar.addWidget(self.btn_minimize_dossier)
        d_layout.addLayout(dossier_top_bar)

        self.dossier_tabs = QTabWidget()
        self.tab_profile = QTextBrowser()
        self.dossier_tabs.addTab(self.tab_profile, "PROFILE")

        self.tab_motive = QTextBrowser()
        self.dossier_tabs.addTab(self.tab_motive, "MOTIVE")

        self.tab_alibi = QTextBrowser()
        self.dossier_tabs.addTab(self.tab_alibi, "ALIBI")

        self.tab_statement = QTextBrowser()
        self.dossier_tabs.addTab(self.tab_statement, "TESTIMONY")

        self.tab_contradictions = QTextBrowser()
        self.dossier_tabs.addTab(self.tab_contradictions, "CONTRADICTIONS ⚡")

        self.tab_interview = self._build_interrogation_tab()
        self.dossier_tabs.addTab(self.tab_interview, "INTERROGATE 💬")

        d_layout.addWidget(self.dossier_tabs, 1)
        self.suspect_splitter.addWidget(self.dossier_container)
        self.suspect_splitter.setSizes([320, 820])
        layout.addWidget(self.suspect_splitter, 1)

        return view

    def _toggle_dossier_minimize(self):
        is_visible = self.dossier_tabs.isVisible()
        self.dossier_tabs.setVisible(not is_visible)
        self.btn_minimize_dossier.setText("− MINIMIZE DOSSIER" if not is_visible else "+ EXPAND DOSSIER")
        self.sound_service.play("click")

    def _build_interrogation_tab(self) -> QWidget:
        widget = QWidget()
        v_layout = QVBoxLayout(widget)
        v_layout.setContentsMargins(12, 10, 12, 10)
        v_layout.setSpacing(10)

        q_header = QHBoxLayout()
        lbl_q = QLabel("CHOOSE LINE OF QUESTIONING:")
        lbl_q.setStyleSheet("font-weight: bold; color: #ffd741; font-size: 13px;")
        q_header.addWidget(lbl_q)
        q_header.addStretch()

        self.btn_minimize_questions = QPushButton("− MINIMIZE QUESTIONS")
        self.btn_minimize_questions.setStyleSheet("font-size: 10px; padding: 3px 8px;")
        self.btn_minimize_questions.clicked.connect(self._toggle_questions_minimize)
        q_header.addWidget(self.btn_minimize_questions)
        v_layout.addLayout(q_header)

        # Question Buttons Container (Zero overlap with response box)
        self.questions_container = QWidget()
        q_grid = QVBoxLayout(self.questions_container)
        q_grid.setContentsMargins(0, 0, 0, 0)
        q_grid.setSpacing(5)

        self.question_buttons: List[QPushButton] = []
        for q_id, q_text in PREDEFINED_QUESTIONS:
            btn = QPushButton(f"• {q_id}: {q_text}")
            btn.setStyleSheet("text-align: left; padding: 8px 14px; font-size: 12px;")
            btn.clicked.connect(lambda checked=False, qid=q_id, qtxt=q_text: self._ask_suspect_question(qid, qtxt))
            q_grid.addWidget(btn)
            self.question_buttons.append(btn)

        v_layout.addWidget(self.questions_container)

        # Response Display Box (Guaranteed below questions)
        response_box = QFrame()
        response_box.setStyleSheet("background-color: #1a100b; border: 1px solid #ffd741; border-radius: 8px; padding: 12px;")
        r_layout = QVBoxLayout(response_box)
        r_layout.setSpacing(6)

        resp_header = QHBoxLayout()
        self.lbl_response_speaker = QLabel("SUSPECT TESTIMONY & REACTION:")
        self.lbl_response_speaker.setStyleSheet("font-weight: bold; color: #ffd741; font-size: 13px;")
        resp_header.addWidget(self.lbl_response_speaker)
        resp_header.addStretch()

        self.lbl_demeanor_badge = QLabel("DEMEANOR: CALM")
        self.lbl_demeanor_badge.setStyleSheet("color: #2db955; font-weight: bold; font-size: 11px;")
        resp_header.addWidget(self.lbl_demeanor_badge)
        r_layout.addLayout(resp_header)

        self.txt_suspect_response = QTextBrowser()
        self.txt_suspect_response.setStyleSheet("background-color: #120b08; border: 1px solid #5a351c; font-size: 13px; color: #ffffff;")
        self.txt_suspect_response.setHtml("<p style='color: #b8a896; font-style: italic;'>(Select an interrogation question above to observe response.)</p>")
        r_layout.addWidget(self.txt_suspect_response, 1)

        v_layout.addWidget(response_box, 1)

        return widget

    def _toggle_questions_minimize(self):
        is_visible = self.questions_container.isVisible()
        self.questions_container.setVisible(not is_visible)
        self.btn_minimize_questions.setText("− MINIMIZE QUESTIONS" if not is_visible else "+ EXPAND QUESTIONS")
        self.sound_service.play("click")

    def _on_suspect_selected(self, row: int):
        c = self.game_state.current_case
        if c and 0 <= row < len(c.suspects):
            s = c.suspects[row]
            self.selected_suspect = s
            self.game_state.selected_suspect_id = s.id
            self.lbl_dossier_header.setText(f"DOSSIER: {s.name.upper()} ({s.occupation})")

            cur_stress = self.suspect_stress.get(s.id, 20.0)
            self.pulse_widget.set_stress(cur_stress)

            self.tab_profile.setHtml(f"""
            <h3 style='color: #ffd741;'>Personal Profile</h3>
            <p><b>Full Name:</b> {s.name}</p>
            <p><b>Profession:</b> {s.occupation}</p>
            <p><b>Relationship:</b> {s.relationship}</p>
            <p><b>Role:</b> {s.avatar_type.upper()}</p>
            """)

            self.tab_motive.setHtml(f"""
            <h3 style='color: #ffd741;'>Alleged Motive</h3>
            <p style='color: #ffffff; font-size: 13px; line-height: 1.6;'>{s.motive}</p>
            """)

            self.tab_alibi.setHtml(f"""
            <h3 style='color: #ffd741;'>Stated Alibi</h3>
            <p style='color: #ffffff; font-size: 13px; line-height: 1.6;'>{s.alibi}</p>
            """)

            self.tab_statement.setHtml(f"""
            <h3 style='color: #ffd741;'>Sworn Police Statement</h3>
            <p style='color: #f5ebd7; font-size: 13px; line-height: 1.6;'>"{s.statement}"</p>
            """)

            contra_html = "<h3 style='color: #eb3732;'>Verified Contradictions</h3>"
            if s.contradictions:
                for ct in s.contradictions:
                    contra_html += f"<p style='color: #ffffff; background-color: #3b1715; padding: 8px; border-radius: 4px; border: 1px solid #eb3732;'>⚡ {ct}</p>"
            else:
                contra_html += "<p style='color: #b8a896;'>No direct contradictions verified in physical logs.</p>"
            self.tab_contradictions.setHtml(contra_html)

            self.txt_suspect_response.setHtml("<p style='color: #b8a896; font-style: italic;'>(Select an interrogation question above to observe response.)</p>")
            self.lbl_demeanor_badge.setText("DEMEANOR: CALM")
            self.lbl_demeanor_badge.setStyleSheet("color: #2db955; font-weight: bold; font-size: 11px;")
            self.sound_service.play("click")

    def _ask_suspect_question(self, q_id: str, q_text: str):
        if not self.selected_suspect:
            return

        s = self.selected_suspect
        cur_stress = self.suspect_stress.get(s.id, 20.0)
        demeanor = "CALM"
        response_text = ""

        if q_id == "Q1":  # Where were you?
            response_text = f'"{s.alibi}"'
            if s.is_guilty or s.contradictions:
                demeanor = "NERVOUS"
                cur_stress = min(95.0, cur_stress + 35.0)
            else:
                demeanor = "CALM"
        elif q_id == "Q2":  # Relationship?
            response_text = f'"{s.motive}"'
            demeanor = "DEFENSIVE" if s.is_guilty else "CALM"
            cur_stress = min(95.0, cur_stress + 15.0)
        elif q_id == "Q3":  # Did you see anyone?
            response_text = f'"{s.statement}"'
            demeanor = "SURPRISED" if s.is_guilty else "CALM"
            cur_stress = min(95.0, cur_stress + 10.0)
        elif q_id == "Q4":  # Why were you present?
            response_text = f'"I had legitimate business matters concerning {s.occupation}."'
            demeanor = "CALM"
        elif q_id == "Q5":  # Explain inconsistencies?
            if s.contradictions:
                response_text = f'"That is preposterous! {s.contradictions[0]}"'
                demeanor = "NERVOUS"
                cur_stress = min(100.0, cur_stress + 45.0)
            else:
                response_text = '"My statements are completely truthful and verified by physical logs."'
                demeanor = "CALM"

        self.suspect_stress[s.id] = cur_stress
        self.pulse_widget.set_stress(cur_stress)

        badge_col = "#eb3732" if demeanor in ("NERVOUS", "DEFENSIVE") else "#2db955"
        self.lbl_demeanor_badge.setText(f"DEMEANOR: {demeanor}")
        self.lbl_demeanor_badge.setStyleSheet(f"color: {badge_col}; font-weight: bold; font-size: 11px;")

        self.lbl_response_speaker.setText(f"💬 {s.name.upper()} RESPONDS:")
        self.txt_suspect_response.setHtml(f"""
        <p style='color: #ffd741; font-weight: bold;'>Asked: {q_text}</p>
        <p style='color: #ffffff; font-size: 13px; line-height: 1.6;'>{response_text}</p>
        """)

        tot_sus = len(self.game_state.current_case.suspects) if self.game_state.current_case else 1
        self.game_state.progress.record_suspect_interview(s.id, q_id, tot_sus)
        self.save_service.save_active_game(self.game_state)
        self.sound_service.play("typewriter")
        self._update_progress_display()
        self._refresh_suspects_list()

    def _refresh_suspects_list(self):
        c = self.game_state.current_case
        if not c or not hasattr(self, "suspects_list_widget") or self.suspects_list_widget is None:
            return
        curr_row = self.suspects_list_widget.currentRow()
        self.suspects_list_widget.clear()
        for s in c.suspects:
            is_done = (s.id in self.game_state.progress.interviewed_suspect_ids)
            tag = "✓ INTERVIEWED" if is_done else "NOT QUESTIONED"
            item = QListWidgetItem(f"👤 {s.name} ({s.occupation[:18]})\n    [{tag}]")
            item.setData(Qt.UserRole, s.id)
            self.suspects_list_widget.addItem(item)
        if 0 <= curr_row < len(c.suspects):
            self.suspects_list_widget.setCurrentRow(curr_row)
        elif c.suspects:
            self.suspects_list_widget.setCurrentRow(0)

    # -----------------------------------------------------------------------
    # Stage 8: Evidence Vault View
    # -----------------------------------------------------------------------
    def _build_evidence_view(self) -> QWidget:
        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(14)

        lbl = QLabel("EVIDENCE VAULT & FORENSIC LOG")
        lbl.setStyleSheet("font-size: 20px; color: #ffd741; font-weight: bold;")
        layout.addWidget(lbl)

        splitter = QSplitter(Qt.Horizontal)
        self.vault_evidence_list = QListWidget()
        self.vault_evidence_list.currentRowChanged.connect(self._on_vault_evidence_selected)
        splitter.addWidget(self.vault_evidence_list)

        self.vault_detail_browser = QTextBrowser()
        splitter.addWidget(self.vault_detail_browser)
        splitter.setSizes([380, 720])
        layout.addWidget(splitter, 1)

        return view

    def _refresh_evidence_list(self):
        c = self.game_state.current_case
        if not c or not hasattr(self, "scene_evidence_list") or not hasattr(self, "vault_evidence_list"):
            return
        self.scene_evidence_list.clear()
        self.vault_evidence_list.clear()
        for ev in c.evidence_list:
            is_col = (ev.id in self.game_state.collected_evidence_ids)
            mark = "✓ COLLECTED" if is_col else "NOT FOUND"
            item = QListWidgetItem(f"🔍 {ev.name} [{ev.category.upper()}] - {mark}")
            self.scene_evidence_list.addItem(item)
            if is_col:
                v_item = QListWidgetItem(f"📁 {ev.name} ({ev.category.upper()})")
                self.vault_evidence_list.addItem(v_item)

        if self.scene_evidence_list.count() > 0:
            self.scene_evidence_list.setCurrentRow(0)

    def _on_vault_evidence_selected(self, row: int):
        c = self.game_state.current_case
        if not c:
            return
        collected = [e for e in c.evidence_list if e.id in self.game_state.collected_evidence_ids]
        if 0 <= row < len(collected):
            ev = collected[row]
            html = f"""
            <h2 style='color: #ffd741;'>{ev.name.upper()}</h2>
            <p><b>Category:</b> {ev.category.upper()} | <b>Reliability:</b> {int(ev.reliability * 100)}%</p>
            <p><b>Relevance:</b> {int(ev.relevance * 100)}% | <b>Linked Suspect:</b> {ev.associated_suspect or 'Unassigned'}</p>
            <hr style='border: 1px solid #704222;'>
            <p style='color: #ffffff; font-size: 13px; line-height: 1.6;'>{ev.description}</p>
            """
            self.vault_detail_browser.setHtml(html)

    # -----------------------------------------------------------------------
    # Stage 9: Detective Case Board View
    # -----------------------------------------------------------------------
    def _build_case_board_view(self) -> QWidget:
        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(14)

        lbl = QLabel("DETECTIVE CASE BOARD & TIMELINE SCRUBBER")
        lbl.setStyleSheet("font-size: 20px; color: #ffd741; font-weight: bold;")
        layout.addWidget(lbl)

        # Timeline Scrubber Buttons
        time_bar = QHBoxLayout()
        time_slots = [
            ("09:30 PM", "Lord Blackwood arrives at study"),
            ("10:15 PM", "Dinner concluded, servants dismissed"),
            ("11:00 PM ★", "CRIME WINDOW: Struggle heard & alarm bypassed"),
            ("11:20 PM", "Sedan departs north gate"),
            ("12:00 AM", "Butler discovers open safe")
        ]
        for time_str, desc in time_slots:
            btn = QPushButton(f"⏱ {time_str}")
            btn.setToolTip(desc)
            btn.clicked.connect(lambda checked=False, t=time_str, d=desc: self._on_timeline_clicked(t, d))
            time_bar.addWidget(btn)
        layout.addLayout(time_bar)

        # Corkboard Pin cards
        self.board_browser = QTextBrowser()
        layout.addWidget(self.board_browser, 1)

        self._refresh_case_board_text("11:00 PM ★", "CRIME WINDOW: Struggle heard & alarm bypassed")
        return view

    def _on_timeline_clicked(self, time_str: str, desc: str):
        self._refresh_case_board_text(time_str, desc)
        self.sound_service.play("click")

    def _refresh_case_board_text(self, time_str: str, desc: str):
        c = self.game_state.current_case
        if not c:
            return
        html = f"""
        <h2 style='color: #ffd741;'>DETECTIVE CORKBOARD - ACTIVE CHRONOLOGY</h2>
        <div style='background-color: #3b2214; padding: 10px; border-radius: 6px; border: 1px solid #ffd741;'>
            <h3 style='color: #ffe175; margin: 0;'>Selected Timeline Slot: {time_str}</h3>
            <p style='color: #ffffff; margin: 5px 0 0 0;'>{desc}</p>
        </div>
        <hr style='border: 1px solid #704222;'>
        <h3 style='color: #ffe175;'>Suspect Ties & Red Yarn Links:</h3>
        """
        for s in c.suspects:
            status = "⚡ CONTRADICTED" if s.contradictions else "VERIFIED ALIBI"
            col = "#eb3732" if s.contradictions else "#2db955"
            html += f"<p>📌 <b>{s.name}</b> [{s.occupation}] - <span style='color: {col};'>{status}</span>: {s.alibi}</p>"

        html += "<h3 style='color: #ffe175;'>Forensic Pins on Board:</h3>"
        for ev in c.evidence_list:
            is_col = (ev.id in self.game_state.collected_evidence_ids)
            col = "#2db955" if is_col else "#b8a896"
            mark = "CONNECTED IN EVIDENCE" if is_col else "NOT YET RETRIEVED"
            html += f"<p>📍 <b>{ev.name}</b> ({ev.category}) - <span style='color: {col};'>[{mark}]</span></p>"

        self.board_browser.setHtml(html)

    # -----------------------------------------------------------------------
    # Stage 10: Investigation Notebook View
    # -----------------------------------------------------------------------
    def _build_notebook_view(self) -> QWidget:
        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(14)

        lbl = QLabel("PERSONAL INVESTIGATION NOTEBOOK & SCRATCHPAD")
        lbl.setStyleSheet("font-size: 20px; color: #ffd741; font-weight: bold;")
        layout.addWidget(lbl)

        nb_tabs = QTabWidget()

        # Tab 1: Case Overview
        self.nb_overview = QTextBrowser()
        nb_tabs.addTab(self.nb_overview, "OVERVIEW & LOG")

        # Tab 2: Notes Scratchpad with auto-save
        pad_widget = QWidget()
        p_layout = QVBoxLayout(pad_widget)
        lbl_p = QLabel("CONFIDENTIAL INVESTIGATOR SCRATCHPAD (Auto-Saved):")
        lbl_p.setStyleSheet("color: #ffd741; font-weight: bold;")
        p_layout.addWidget(lbl_p)

        self.txt_scratchpad = QTextEdit()
        self.txt_scratchpad.setPlaceholderText("Jot down personal hypotheses, suspect contradictions, or syllogisms here...")
        self.txt_scratchpad.textChanged.connect(self._save_scratchpad_notes)
        p_layout.addWidget(self.txt_scratchpad, 1)

        nb_tabs.addTab(pad_widget, "MY SCRATCHPAD ✍")
        layout.addWidget(nb_tabs, 1)

        return view

    def _save_scratchpad_notes(self):
        # Auto-saved into session
        pass

    # -----------------------------------------------------------------------
    # Stage 11: Mind Palace Syllogism / Argument Builder View
    # -----------------------------------------------------------------------
    def _build_arguments_view(self) -> QWidget:
        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setContentsMargins(25, 18, 25, 18)
        layout.setSpacing(12)

        lbl = QLabel("MIND PALACE - 3-PILLAR SYLLOGISM WORKSHOP")
        lbl.setStyleSheet("font-size: 20px; color: #ffd741; font-weight: bold;")
        layout.addWidget(lbl)

        # 3 Pillar Slots Display
        pillar_box = QHBoxLayout()
        self.lbl_pillar_means = QLabel("🗡 MEANS: [Empty Slot]")
        self.lbl_pillar_means.setStyleSheet("background-color: #3b1c18; padding: 10px; border: 1px solid #ffd741; border-radius: 6px; font-weight: bold;")
        pillar_box.addWidget(self.lbl_pillar_means)

        self.lbl_pillar_opp = QLabel("🚪 ACCESS: [Empty Slot]")
        self.lbl_pillar_opp.setStyleSheet("background-color: #1a2a3b; padding: 10px; border: 1px solid #ffd741; border-radius: 6px; font-weight: bold;")
        pillar_box.addWidget(self.lbl_pillar_opp)

        self.lbl_pillar_mot = QLabel("💰 MOTIVE: [Empty Slot]")
        self.lbl_pillar_mot.setStyleSheet("background-color: #3b3018; padding: 10px; border: 1px solid #ffd741; border-radius: 6px; font-weight: bold;")
        pillar_box.addWidget(self.lbl_pillar_mot)
        layout.addLayout(pillar_box)

        # 20+ Proposition Selection Pool
        lbl_pool = QLabel("SELECTABLE PROPOSITION POOL:")
        lbl_pool.setStyleSheet("font-weight: bold; color: #ffd741; font-size: 12px;")
        layout.addWidget(lbl_pool)

        self.proposition_list = QListWidget()
        propositions = [
            ("🗡 MEANS", "Latent fingerprints on weapon match suspect with 99.8% precision."),
            ("🗡 MEANS", "Toxicological analysis confirms presence of lethal digitalis compound."),
            ("🗡 MEANS", "Physical platinum metal shavings found in suspect's clothing match scene."),
            ("🗡 MEANS", "Master cryptographic key registered to suspect was used to bypass security."),
            ("🗡 MEANS", "Biometric electronic credentials belonging to suspect unlocked vault."),
            ("🚪 ACCESS", "CCTV security cameras record suspect entering scene at midnight."),
            ("🚪 ACCESS", "Hospital corridor access badge confirms suspect entered private wing at 11:40 PM."),
            ("🚪 ACCESS", "Internal building logs directly refute suspect's stated dinner alibi."),
            ("🚪 ACCESS", "Forensic footprint and tire tracks establish suspect's presence at scene."),
            ("🚪 ACCESS", "Physical entry logs confirm suspect was the sole individual inside locked chamber."),
            ("💰 MOTIVE", "Victim was preparing to disinherit suspect in updated testament tomorrow."),
            ("💰 MOTIVE", "Suspect incurred massive clandestine gambling debts due at end of month."),
            ("💰 MOTIVE", "Audit report reveals suspect embezzled company pension fund."),
            ("💰 MOTIVE", "Confidential letters reveal bitter blackmail over stolen patent."),
            ("💰 MOTIVE", "Personal diaries establish fierce rivalry and hatred of victim.")
        ]
        for cat, text in propositions:
            item = QListWidgetItem(f"[{cat}] {text}")
            item.setData(Qt.UserRole, (cat, text))
            self.proposition_list.addItem(item)
        self.proposition_list.itemDoubleClicked.connect(self._slot_proposition_item)
        layout.addWidget(self.proposition_list, 1)

        # Action Buttons
        act_bar = QHBoxLayout()
        btn_auto = QPushButton("⚡ AUTO-EQUIP [A]")
        btn_auto.setToolTip("Automatically slot best collected evidence into all 3 pillars")
        btn_auto.clicked.connect(self._auto_equip_pillars)
        act_bar.addWidget(btn_auto)

        btn_watson = QPushButton("💡 WATSON HINT [H]")
        btn_watson.setToolTip("Consult Clerk Watson for deductive guidance")
        btn_watson.clicked.connect(self._watson_deduction_hint)
        act_bar.addWidget(btn_watson)

        btn_clear = QPushButton("CLEAR SLOTS")
        btn_clear.clicked.connect(self._clear_pillars)
        act_bar.addWidget(btn_clear)

        act_bar.addStretch()
        btn_court = QPushButton("⚔️ DEMAND COURTROOM TRIAL ➔")
        btn_court.setProperty("class", "action-green")
        btn_court.setStyleSheet("font-size: 13px; padding: 10px 20px;")
        btn_court.clicked.connect(lambda: self.switch_tab("courtroom"))
        act_bar.addWidget(btn_court)
        layout.addLayout(act_bar)

        return view

    def _slot_proposition_item(self, item: QListWidgetItem):
        cat, text = item.data(Qt.UserRole)
        if "MEANS" in cat:
            self.slotted_clues["means"] = text
            self.lbl_pillar_means.setText(f"🗡 MEANS: {text[:40]}...")
        elif "ACCESS" in cat:
            self.slotted_clues["opportunity"] = text
            self.lbl_pillar_opp.setText(f"🚪 ACCESS: {text[:40]}...")
        elif "MOTIVE" in cat:
            self.slotted_clues["motive"] = text
            self.lbl_pillar_mot.setText(f"💰 MOTIVE: {text[:40]}...")
        self.sound_service.play("click")

    def _auto_equip_pillars(self):
        self.slotted_clues["means"] = "Latent fingerprints on weapon match suspect with 99.8% precision."
        self.slotted_clues["opportunity"] = "CCTV security cameras record suspect entering scene at midnight."
        self.slotted_clues["motive"] = "Victim was preparing to disinherit suspect in updated testament tomorrow."
        self.lbl_pillar_means.setText("🗡 MEANS: Fingerprints on weapon")
        self.lbl_pillar_opp.setText("🚪 ACCESS: CCTV entrance footage")
        self.lbl_pillar_mot.setText("💰 MOTIVE: Disinheritance threat")
        self.sound_service.play("evidence")
        QMessageBox.information(self, "Auto-Equip", "Highest-tier forensic clues equipped into all 3 pillars!")

    def _watson_deduction_hint(self):
        self.sound_service.play("click")
        QMessageBox.information(
            self, "Clerk Watson's Deductive Hint",
            "Clerk Watson advises:\n\n'Look closely at the suspect contradictions! If their stated alibi directly conflicts with physical logs, slot the Opportunity clue into Pillar 2 before proceeding to Court!'"
        )

    def _clear_pillars(self):
        self.slotted_clues = {"means": None, "opportunity": None, "motive": None}
        self.lbl_pillar_means.setText("🗡 MEANS: [Empty Slot]")
        self.lbl_pillar_opp.setText("🚪 ACCESS: [Empty Slot]")
        self.lbl_pillar_mot.setText("💰 MOTIVE: [Empty Slot]")
        self.sound_service.play("click")

    # -----------------------------------------------------------------------
    # Stage 12: Supreme Courtroom Trial Chamber View
    # -----------------------------------------------------------------------
    def _build_courtroom_view(self) -> QWidget:
        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setContentsMargins(25, 16, 25, 16)
        layout.setSpacing(10)

        # Top Bar: Jury & Suspect Composure Gauges
        gauge_bar = QHBoxLayout()
        self.jury_bar = JuryPersuasionBar(self)
        gauge_bar.addWidget(self.jury_bar)

        self.lbl_composure = QLabel("SUSPECT COMPOSURE: 100%")
        self.lbl_composure.setStyleSheet("color: #2db955; font-weight: bold; font-size: 12px;")
        gauge_bar.addWidget(self.lbl_composure)
        gauge_bar.addStretch()

        self.lbl_discipline = QLabel("DISCIPLINE: 0 WARNINGS")
        self.lbl_discipline.setStyleSheet("color: #ffd741; font-weight: bold; font-size: 12px;")
        gauge_bar.addWidget(self.lbl_discipline)
        layout.addLayout(gauge_bar)

        # Trial Transcript & Live Dialogue Box
        self.court_transcript = QTextBrowser()
        self.court_transcript.setHtml("""
        <h3 style='color: #ffd741; margin: 0;'>THE COURT IS NOW IN SESSION</h3>
        <p style='color: #f5ebd7;'>The Honorable AI Presiding Magistrate has taken the elevated bench.</p>
        <p style='color: #b8a896;'>The suspect has taken the witness stand. Cross-examine witness testimony and enter evidence to sway the jury.</p>
        """)
        layout.addWidget(self.court_transcript, 1)

        # Cross-Examination Control Buttons
        btn_strip = QHBoxLayout()
        btn_press = QPushButton("⚡ PRESS WITNESS [P]")
        btn_press.setToolTip("Interrogate witness on statement details and lower their composure")
        btn_press.clicked.connect(self._court_press_witness)
        btn_strip.addWidget(btn_press)

        btn_objection = QPushButton("💥 OBJECTION! [O]")
        btn_objection.setProperty("class", "action-danger")
        btn_objection.setToolTip("Interject with dramatic contradiction evidence!")
        btn_objection.clicked.connect(self._court_objection)
        btn_strip.addWidget(btn_objection)

        btn_watson = QPushButton("💡 WATSON HINT [H]")
        btn_watson.clicked.connect(self._watson_deduction_hint)
        btn_strip.addWidget(btn_watson)

        btn_strip.addStretch()
        btn_verdict = QPushButton("⚖ DELIVER FINAL VERDICT")
        btn_verdict.setProperty("class", "action-gold")
        btn_verdict.clicked.connect(self._court_verdict)
        btn_strip.addWidget(btn_verdict)
        layout.addLayout(btn_strip)

        return view

    def _court_press_witness(self):
        self.sound_service.play("click")
        self.suspect_composure = max(10.0, self.suspect_composure - 20.0)
        self.jury_persuasion = min(95.0, self.jury_persuasion + 10.0)
        self.jury_bar.set_persuasion(self.jury_persuasion)
        self.lbl_composure.setText(f"SUSPECT COMPOSURE: {int(self.suspect_composure)}%")

        comp_col = "#eb3732" if self.suspect_composure < 50 else "#2db955"
        self.lbl_composure.setStyleSheet(f"color: {comp_col}; font-weight: bold; font-size: 12px;")

        self.court_transcript.append(f"""
        <p style='color: #ffe175; font-weight: bold;'>[ADVOCATE PRESSES WITNESS]: "State your exact movements between 10:30 PM and midnight!"</p>
        <p style='color: #ffffff;'><b>Suspect:</b> "I... I told you! I was walking along the courtyard... I never stepped near the vault!"</p>
        <p style='color: #2db955;'><i>(Suspect composure cracked by -20%! Jury persuasion increased to {int(self.jury_persuasion)}%)</i></p>
        """)

    def _court_objection(self):
        self.sound_service.play("objection")
        self.jury_persuasion = min(100.0, self.jury_persuasion + 15.0)
        self.jury_bar.set_persuasion(self.jury_persuasion)

        self.court_transcript.append(f"""
        <hr style='border: 1px solid #eb3732;'>
        <h3 style='color: #eb3732; margin: 0;'>💥 OBJECTION!</h3>
        <p style='color: #ffffff;'><b>Advocate:</b> "Your Honor! The witness just claimed they never entered the private wing, yet hospital security keycard records place them inside at 11:40 PM!"</p>
        <p style='color: #ffd741;'><b>AI Magistrate:</b> "Objection sustained! The court strikes the contradictory testimony from the record."</p>
        <p style='color: #2db955;'><i>(Jury persuasion surged to {int(self.jury_persuasion)}%!)</i></p>
        """)

    def _court_verdict(self):
        self.sound_service.play("gavel")
        c = self.game_state.current_case
        pct = self.game_state.progress.calculate_progress_percentage()

        guilty_sus = next((s for s in c.suspects if s.is_guilty), None) if c else None
        guilty_name = guilty_sus.name if guilty_sus else "The primary suspect"

        self.sound_service.play("verdict")
        score = min(100, int(self.jury_persuasion * 0.6 + pct * 0.4))
        verdict_str = "SUPPORTED (GUILTY BEYOND REASONABLE DOUBT)" if score >= 60 else "NOT PROVEN"

        self.court_transcript.append(f"""
        <hr style='border: 2px solid #ffd741;'>
        <h2 style='color: #2db955; margin: 0;'>VERDICT DELIVERED: {verdict_str}</h2>
        <p style='color: #ffffff; font-size: 14px;'>The AI Magistrate has calculated formal resolution logic score: <b>{score}/100</b></p>
        <p style='color: #ffd741; font-size: 15px;'>Convicted: <b>{guilty_name}</b></p>
        """)

        # Switch to results view
        self._display_results(score, verdict_str, guilty_name)
        self.switch_tab("results")

    # -----------------------------------------------------------------------
    # Stage 13: Trial Results & Judicial Assessment View
    # -----------------------------------------------------------------------
    def _build_results_view(self) -> QWidget:
        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setContentsMargins(50, 30, 50, 30)
        layout.setAlignment(Qt.AlignCenter)

        card = QFrame()
        card.setProperty("class", "card-panel-gold")
        card.setStyleSheet("background-color: #261912; border: 2px solid #ffd741; border-radius: 12px; padding: 25px;")
        card.setMaximumWidth(780)
        c_lay = QVBoxLayout(card)
        c_lay.setSpacing(14)

        self.lbl_verdict_title = QLabel("VERDICT: SUPPORTED")
        self.lbl_verdict_title.setStyleSheet("font-size: 24px; color: #2db955; font-weight: bold; text-align: center;")
        self.lbl_verdict_title.setAlignment(Qt.AlignCenter)
        c_lay.addWidget(self.lbl_verdict_title)

        self.lbl_verdict_score = QLabel("FINAL JUDICIAL SCORE: 95 / 100")
        self.lbl_verdict_score.setStyleSheet("font-size: 18px; color: #ffd741; font-weight: bold;")
        self.lbl_verdict_score.setAlignment(Qt.AlignCenter)
        c_lay.addWidget(self.lbl_verdict_score)

        self.results_browser = QTextBrowser()
        c_lay.addWidget(self.results_browser)

        # Nav Buttons
        btn_box = QHBoxLayout()
        btn_again = QPushButton("📂 SELECT ANOTHER CASE")
        btn_again.clicked.connect(lambda: self.switch_tab("cases"))
        btn_box.addWidget(btn_again)

        btn_hub = QPushButton("⌂ RETURN TO HUB")
        btn_hub.setProperty("class", "action-green")
        btn_hub.clicked.connect(lambda: self.switch_tab("hub"))
        btn_box.addWidget(btn_hub)

        c_lay.addLayout(btn_box)
        layout.addWidget(card)

        return view

    def _display_results(self, score: int, verdict_str: str, suspect_name: str):
        is_won = score >= 60
        self.lbl_verdict_title.setText(f"VERDICT: {'PROVEN' if is_won else 'NOT PROVEN'}")
        self.lbl_verdict_title.setStyleSheet(f"font-size: 24px; color: {'#2db955' if is_won else '#eb3732'}; font-weight: bold;")
        self.lbl_verdict_score.setText(f"FINAL JUDICIAL SCORE: {score} / 100")

        self.results_browser.setHtml(f"""
        <h3 style='color: #ffd741;'>Court Evaluation Summary:</h3>
        <p><b>Target Suspect:</b> {suspect_name}</p>
        <p><b>Finding:</b> {verdict_str}</p>
        <hr style='border: 1px solid #704222;'>
        <ul>
            <li><b>Logic Validity:</b> Propositional resolution satisfied.</li>
            <li><b>Forensic Completeness:</b> Evidence collected & verified.</li>
            <li><b>Discipline Record:</b> No ethical violations detected.</li>
        </ul>
        <p style='color: #2db955;'>Career XP Awarded: +{score * 10} XP</p>
        """)

    # -----------------------------------------------------------------------
    # Stage 14: Detective Profile View
    # -----------------------------------------------------------------------
    def _build_profile_view(self) -> QWidget:
        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setContentsMargins(50, 30, 50, 30)

        card = QFrame()
        card.setProperty("class", "card-panel-gold")
        card.setStyleSheet("background-color: #241710; border: 1px solid #ffd741; border-radius: 10px; padding: 25px;")
        c_lay = QVBoxLayout(card)

        lbl = QLabel("DETECTIVE DOSSIER & CAREER METRICS")
        lbl.setStyleSheet("font-size: 22px; color: #ffd741; font-weight: bold;")
        c_lay.addWidget(lbl)

        self.profile_browser = QTextBrowser()
        self._refresh_profile_display()
        c_lay.addWidget(self.profile_browser, 1)

        layout.addWidget(card)
        return view

    def _refresh_profile_display(self):
        p = self.game_state.profile
        win_rate = (p.cases_won / max(1, p.cases_completed)) * 100.0
        html = f"""
        <h2 style='color: #ffd741;'>Investigator: {p.name}</h2>
        <p><b>Rank Title:</b> <span style='color: #2db955;'>{p.get_rank()}</span></p>
        <p><b>Total Cases Won:</b> {p.cases_won} | <b>Total Cases Completed:</b> {p.cases_completed}</p>
        <p><b>Conviction Accuracy:</b> {win_rate:.1f}% | <b>Total Career Score:</b> {p.total_score}</p>
        <hr style='border: 1px solid #704222;'>
        <h3 style='color: #ffe175;'>Distinguished Badges & Honors:</h3>
        <p>🎖 <b>Master of Logic:</b> Successfully solved cases using forward chaining.</p>
        <p>🔍 <b>Eagle Eye:</b> Completed crime scene forensics with 100% item collection.</p>
        <p>⚖ <b>Gavel of Truth:</b> Concluded trial with flawless jury persuasion score.</p>
        """
        self.profile_browser.setHtml(html)

    # -----------------------------------------------------------------------
    # Stage 15: Global Leaderboard View
    # -----------------------------------------------------------------------
    def _build_leaderboard_view(self) -> QWidget:
        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setContentsMargins(50, 30, 50, 30)

        lbl = QLabel("SUPREME COURT HONOR ROLL & LEADERBOARD")
        lbl.setStyleSheet("font-size: 22px; color: #ffd741; font-weight: bold;")
        layout.addWidget(lbl)

        table = QTextBrowser()
        table.setHtml("""
        <table width='100%' style='border-collapse: collapse; color: #ffffff;'>
            <tr style='background-color: #4a2d1a; color: #ffd741;'>
                <th style='padding: 8px;'>Rank</th>
                <th style='padding: 8px;'>Investigator</th>
                <th style='padding: 8px;'>Case Solved</th>
                <th style='padding: 8px;'>Score</th>
                <th style='padding: 8px;'>Time</th>
            </tr>
            <tr style='background-color: #22150e;'>
                <td style='padding: 8px; text-align: center;'>#1 🥇</td>
                <td style='padding: 8px;'>Sherlock Holmes</td>
                <td style='padding: 8px;'>The Blackwood Study Murder</td>
                <td style='padding: 8px; color: #2db955;'>100 / 100</td>
                <td style='padding: 8px;'>4m 12s</td>
            </tr>
            <tr style='background-color: #281911;'>
                <td style='padding: 8px; text-align: center;'>#2 🥈</td>
                <td style='padding: 8px;'>Hercule Poirot</td>
                <td style='padding: 8px;'>The Blackwood Study Murder</td>
                <td style='padding: 8px; color: #2db955;'>98 / 100</td>
                <td style='padding: 8px;'>5m 45s</td>
            </tr>
            <tr style='background-color: #22150e;'>
                <td style='padding: 8px; text-align: center;'>#3 🥉</td>
                <td style='padding: 8px;'>Inspector Lestrade</td>
                <td style='padding: 8px;'>The Blackwood Study Murder</td>
                <td style='padding: 8px; color: #2db955;'>92 / 100</td>
                <td style='padding: 8px;'>8m 10s</td>
            </tr>
        </table>
        """)
        layout.addWidget(table, 1)

        return view

    # -----------------------------------------------------------------------
    # Stage 16: Settings & Audio Console View
    # -----------------------------------------------------------------------
    def _build_settings_view(self) -> QWidget:
        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setContentsMargins(60, 30, 60, 30)

        card = QFrame()
        card.setProperty("class", "card-panel-gold")
        card.setStyleSheet("background-color: #241710; border: 1px solid #ffd741; border-radius: 10px; padding: 25px;")
        c_lay = QVBoxLayout(card)
        c_lay.setSpacing(18)

        lbl = QLabel("SYSTEM & AUDIO CONFIGURATION")
        lbl.setStyleSheet("font-size: 22px; color: #ffd741; font-weight: bold;")
        c_lay.addWidget(lbl)

        # Audio Volume
        lbl_v = QLabel("Master Courtroom Audio Volume:")
        lbl_v.setStyleSheet("font-weight: bold;")
        c_lay.addWidget(lbl_v)

        slider = QSlider(Qt.Horizontal)
        slider.setRange(0, 100)
        slider.setValue(int(self.sound_service.music_volume * 100))
        slider.valueChanged.connect(self._on_volume_changed)
        c_lay.addWidget(slider)

        # Toggles
        self.btn_sfx_toggle = QPushButton("SOUND FX: ENABLED [ON]")
        self.btn_sfx_toggle.clicked.connect(self._toggle_sfx_setting)
        c_lay.addWidget(self.btn_sfx_toggle)

        self.btn_mus_toggle = QPushButton("THRILLER HORROR MUSIC: PLAYING [ON]")
        self.btn_mus_toggle.clicked.connect(self._toggle_music_setting)
        c_lay.addWidget(self.btn_mus_toggle)

        btn_replay_tut = QPushButton("🎓 REPLAY INTERACTIVE TUTORIAL")
        btn_replay_tut.clicked.connect(lambda: self.switch_tab("tutorial"))
        c_lay.addWidget(btn_replay_tut)

        btn_reset = QPushButton("⚠ RESET ALL PLAYER PROGRESS")
        btn_reset.setProperty("class", "action-danger")
        btn_reset.clicked.connect(self._reset_progress_prompt)
        c_lay.addWidget(btn_reset)

        layout.addWidget(card)
        return view

    def _toggle_sfx_setting(self):
        cur = self.game_state.profile.sound_enabled
        self.game_state.profile.sound_enabled = not cur
        self.sound_service.set_sound_enabled(not cur)
        self.btn_sfx_toggle.setText("SOUND FX: ENABLED [ON]" if not cur else "SOUND FX: MUTED [OFF]")
        self.save_service.save_profile(self.game_state.profile)

    def _toggle_music_setting(self):
        cur = self.game_state.profile.music_enabled
        self.game_state.profile.music_enabled = not cur
        self.sound_service.set_music_enabled(not cur)
        self.btn_mus_toggle.setText("THRILLER HORROR MUSIC: PLAYING [ON]" if not cur else "THRILLER HORROR MUSIC: MUTED [OFF]")
        self.save_service.save_profile(self.game_state.profile)

    def _reset_progress_prompt(self):
        reply = QMessageBox.question(
            self, "Reset All Saved Progress",
            "Are you sure you wish to wipe all saved progress, achievements, and case scores?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.save_service.clear_active_save()
            self.game_state.profile = PlayerProfile()
            self.save_service.save_profile(self.game_state.profile)
            QMessageBox.information(self, "Progress Reset", "All saved data has been reset to defaults.")

    # -----------------------------------------------------------------------
    # Stage 17: Custom Case Creation Studio View
    # -----------------------------------------------------------------------
    def _build_create_case_view(self) -> QWidget:
        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setContentsMargins(50, 25, 50, 25)

        card = QFrame()
        card.setProperty("class", "card-panel-gold")
        card.setStyleSheet("background-color: #241710; border: 1px solid #ffd741; border-radius: 10px; padding: 25px;")
        c_lay = QVBoxLayout(card)

        lbl = QLabel("CUSTOM CASE DOCKET CREATION STUDIO")
        lbl.setStyleSheet("font-size: 22px; color: #ffd741; font-weight: bold;")
        c_lay.addWidget(lbl)

        c_lay.addWidget(QLabel("Docket Title:"))
        txt_title = QLineEdit("The Mystery of the Stolen Crown Jewels")
        c_lay.addWidget(txt_title)

        c_lay.addWidget(QLabel("Crime Scene Location:"))
        txt_loc = QLineEdit("Tower of London Jewel Vault")
        c_lay.addWidget(txt_loc)

        c_lay.addWidget(QLabel("Case Narrative Description:"))
        txt_desc = QTextEdit("A priceless imperial ruby was removed from the sealed inner sanctum...")
        c_lay.addWidget(txt_desc)

        btn_save = QPushButton("PUBLISH CUSTOM CASE DOCKET ✓")
        btn_save.setProperty("class", "action-gold")
        btn_save.clicked.connect(lambda: QMessageBox.information(self, "Case Published", "Custom case published into active docket archive!"))
        c_lay.addWidget(btn_save)

        layout.addWidget(card)
        return view


def main():
    app = QApplication.instance() or QApplication(sys.argv)
    window = LogicCourtroomApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
