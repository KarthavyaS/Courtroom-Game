"""Case Selection Docket Screen for PySide6 LOGIC COURTROOM.
"""

from typing import Optional, List
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget,
    QListWidgetItem, QFrame, QSplitter, QTextBrowser
)
from models.case import Case
from services.game_state import GameState
from services.case_service import CaseService
from services.save_service import SaveService
from app_qt.config import (
    HEX_GOLD, HEX_GOLD_LIGHT, HEX_ACCENT_GREEN, HEX_ACCENT_RED,
    HEX_LIGHT_PARCHMENT, HEX_MUTED_TEXT
)
from app_qt.dialogs.case_preview_dialog import CasePreviewDialogQt
from app_qt.services.sound_service_qt import get_sound_service_qt


class CaseSelectionScreenQt(QWidget):
    """Court docket screen with difficulty filters, preview pane and launch actions."""

    navigate = Signal(str)
    notify = Signal(str, str)
    case_selected = Signal(object)  # Emits selected Case
    back_to_dashboard = Signal()

    def __init__(self, game_state: Optional[GameState] = None, case_service: Optional[CaseService] = None, save_service: Optional[SaveService] = None, parent=None):
        super().__init__(parent)
        self.game_state = game_state or GameState()
        self.case_service = case_service or CaseService()
        self.save_service = save_service or SaveService()
        self.sound_service = get_sound_service_qt()

        self.cases: List[Case] = []
        self.active_filter = "ALL"
        self.selected_case: Optional[Case] = None

        self._build_ui()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 20, 30, 20)
        main_layout.setSpacing(14)

        # Header Bar
        top_bar = QHBoxLayout()
        btn_back = QPushButton("← DASHBOARD")
        btn_back.setStyleSheet("background-color: #3b251a; border: 1px solid #704222; padding: 6px 14px;")
        btn_back.clicked.connect(self._on_back)
        top_bar.addWidget(btn_back)

        lbl_title = QLabel("COURT DOCKET — CASE SELECTION ARCHIVE")
        lbl_title.setProperty("class", "title-gold")
        top_bar.addWidget(lbl_title)
        top_bar.addStretch(1)
        main_layout.addLayout(top_bar)

        # Filter Tabs Row
        filter_bar = QHBoxLayout()
        filter_bar.setSpacing(8)
        self.filter_buttons = {}

        filters = [
            ("ALL", "ALL CASES"),
            ("EASY", "🟢 EASY"),
            ("MEDIUM", "🟡 MEDIUM"),
            ("HARD", "🔴 HARD"),
            ("IN_PROGRESS", "IN PROGRESS"),
            ("COMPLETED", "COMPLETED")
        ]

        for fid, flabel in filters:
            btn = QPushButton(flabel)
            btn.setProperty("class", "btn-nav")
            btn.clicked.connect(lambda checked=False, f=fid: self._on_filter_changed(f))
            self.filter_buttons[fid] = btn
            filter_bar.addWidget(btn)

        filter_bar.addStretch(1)
        main_layout.addLayout(filter_bar)

        # Main Splitter: Left Case List, Right Detailed Preview
        splitter = QSplitter(Qt.Horizontal)

        # Left Case List
        left_frame = QFrame()
        left_frame.setProperty("class", "court-panel")
        l_layout = QVBoxLayout(left_frame)
        l_layout.setContentsMargins(8, 8, 8, 8)

        lbl_list = QLabel("SELECT A CASE FILE:")
        lbl_list.setStyleSheet(f"font-size: 11px; font-weight: bold; color: {HEX_GOLD};")
        l_layout.addWidget(lbl_list)

        self.case_list_widget = QListWidget()
        self.case_list_widget.currentRowChanged.connect(self._on_case_row_changed)
        self.case_list_widget.itemDoubleClicked.connect(self._on_case_double_clicked)
        l_layout.addWidget(self.case_list_widget, 1)
        splitter.addWidget(left_frame)

        # Right Preview Panel
        right_panel = QFrame()
        right_panel.setProperty("class", "court-card-gold")
        right_panel.setStyleSheet("background-color: #241710; border: 1px solid #ffd741; border-radius: 8px; padding: 14px;")
        r_layout = QVBoxLayout(right_panel)
        r_layout.setSpacing(12)

        self.lbl_preview_title = QLabel("SELECT A CASE DOCKET")
        self.lbl_preview_title.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {HEX_GOLD};")
        r_layout.addWidget(self.lbl_preview_title)

        self.preview_browser = QTextBrowser()
        self.preview_browser.setStyleSheet("background-color: #19100c; border: 1px solid #5a351c; border-radius: 6px; padding: 12px;")
        r_layout.addWidget(self.preview_browser, 1)

        self.btn_investigate = QPushButton("COMMENCE INVESTIGATION ➔")
        self.btn_investigate.setProperty("class", "btn-success")
        self.btn_investigate.setFixedHeight(42)
        self.btn_investigate.clicked.connect(self._on_commence_investigation)
        r_layout.addWidget(self.btn_investigate)

        splitter.addWidget(right_panel)
        splitter.setSizes([380, 720])
        main_layout.addWidget(splitter, 1)

    def on_enter_screen(self):
        self.cases = self.case_service.get_all_cases()
        self._refresh_list()

    def _on_filter_changed(self, filter_id: str):
        self.active_filter = filter_id
        self.sound_service.play("click")
        self._refresh_list()

    def _refresh_list(self):
        # Update tab styling
        for fid, btn in self.filter_buttons.items():
            if fid == self.active_filter:
                btn.setStyleSheet(f"background-color: #965f23; border: 1px solid {HEX_GOLD}; color: #ffffff;")
            else:
                btn.setStyleSheet("background-color: #291a13; border: 1px solid #633c22; color: #d8c8b8;")

        self.case_list_widget.clear()
        active_save = self.save_service.load_active_game()
        active_id = active_save.get("case_id") if active_save else None
        completed_ids = [r.get("case_id") for r in self.save_service.get_leaderboard() if r.get("verdict") == "SUPPORTED"]

        filtered = []
        for c in self.cases:
            diff = (c.difficulty or "").upper()
            if self.active_filter == "ALL":
                filtered.append(c)
            elif self.active_filter in ("EASY", "MEDIUM", "HARD") and diff == self.active_filter:
                filtered.append(c)
            elif self.active_filter == "IN_PROGRESS" and c.id == active_id:
                filtered.append(c)
            elif self.active_filter == "COMPLETED" and c.id in completed_ids:
                filtered.append(c)

        for c in filtered:
            status = ""
            if c.id == active_id:
                status = " [ACTIVE]"
            elif c.id in completed_ids:
                status = " [SOLVED ✓]"

            item = QListWidgetItem(f"⚖ {c.title} [{c.difficulty.upper()}]{status}")
            item.setData(Qt.UserRole, c)
            self.case_list_widget.addItem(item)

        if self.case_list_widget.count() > 0:
            self.case_list_widget.setCurrentRow(0)
        else:
            self.selected_case = None
            self.lbl_preview_title.setText("NO CASES IN THIS FILTER")
            self.preview_browser.setHtml("<p style='color: #c8b9aa;'>No criminal cases match the active filter criteria.</p>")
            self.btn_investigate.setEnabled(False)

    def _on_case_row_changed(self, row: int):
        if row >= 0:
            item = self.case_list_widget.item(row)
            if item:
                case = item.data(Qt.UserRole)
                if case:
                    self.selected_case = case
                    self._update_preview(case)
                    self.btn_investigate.setEnabled(True)

    def _update_preview(self, c: Case):
        self.lbl_preview_title.setText(c.title.upper())
        html = f"""
        <h3 style='color: #ffd741; margin-top: 0;'>{c.title}</h3>
        <p><b>Investigation:</b> {c.type.upper()}  |  <b>Location:</b> {c.scene_name}  |  <b>Difficulty:</b> {c.difficulty.upper()}</p>
        <p><b>Judicial Honor Reward:</b> {c.reward} XP</p>
        <hr style='border: 1px solid #704222;'>
        <h4 style='color: #ffeb82;'>Incident Narrative:</h4>
        <p style='color: #f5ebd7; font-size: 13px; line-height: 1.6;'>{c.description}</p>
        <h4 style='color: #ffeb82;'>Suspects Indicted ({len(c.suspects)}):</h4>
        <ul>
        """
        for s in c.suspects:
            html += f"<li><b>{s.name}</b> — {s.occupation} ({s.relationship})</li>"
        html += f"""
        </ul>
        <h4 style='color: #ffeb82;'>Forensic Clues at Scene ({len(c.evidence_list)}):</h4>
        <p style='color: #d8c8b8; font-size: 12px;'>Explore the interactive 2D room to uncover autopsy findings, weapons, and alibi logs.</p>
        """
        self.preview_browser.setHtml(html)

    def _on_case_double_clicked(self, item: QListWidgetItem):
        case = item.data(Qt.UserRole)
        if case:
            self.selected_case = case
            self._on_commence_investigation()

    def _on_commence_investigation(self):
        if self.selected_case:
            dialog = CasePreviewDialogQt(self.selected_case, self)
            if dialog.exec():
                self.sound_service.play("gavel")
                self.game_state.set_case(self.selected_case)
                self.save_service.save_active_game(self.game_state)
                self.case_selected.emit(self.selected_case)
                self.navigate.emit("briefing")

    def _on_back(self):
        self.sound_service.play("click")
        self.back_to_dashboard.emit()
        self.navigate.emit("dashboard")
