"""Forensic Evidence Vault & Review Dashboard for PySide6 LOGIC COURTROOM.
"""

from typing import Optional, List
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget,
    QListWidgetItem, QFrame, QSplitter, QTextBrowser
)
from models.evidence import Evidence
from services.game_state import GameState
from services.save_service import SaveService
from app_qt.config import (
    HEX_GOLD, HEX_GOLD_LIGHT, HEX_ACCENT_GREEN, HEX_ACCENT_BLUE,
    HEX_LIGHT_PARCHMENT, HEX_MUTED_TEXT
)
from app_qt.services.sound_service_qt import get_sound_service_qt


class EvidenceViewScreenQt(QWidget):
    """Evidence review dashboard with categorization and reliability metrics."""

    navigate = Signal(str)
    notify = Signal(str, str)
    proceed_to_board = Signal()

    def __init__(self, game_state: GameState, save_service: SaveService, parent=None):
        super().__init__(parent)
        self.game_state = game_state
        self.save_service = save_service
        self.sound_service = get_sound_service_qt()

        self.active_category = "ALL"
        self.selected_evidence: Optional[Evidence] = None

        self._build_ui()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 14, 25, 14)
        main_layout.setSpacing(12)

        # Header Bar
        top_bar = QHBoxLayout()
        lbl_title = QLabel("FORENSIC EVIDENCE VAULT & LOGICAL ANALYSIS")
        lbl_title.setProperty("class", "title-gold")
        top_bar.addWidget(lbl_title)
        top_bar.addStretch(1)

        btn_proceed = QPushButton("CASE BOARD ➔")
        btn_proceed.setProperty("class", "btn-gold")
        btn_proceed.setFixedHeight(34)
        btn_proceed.clicked.connect(self._on_proceed)
        top_bar.addWidget(btn_proceed)
        main_layout.addLayout(top_bar)

        # Filter Tabs Row
        filter_bar = QHBoxLayout()
        filter_bar.setSpacing(6)
        self.filter_buttons = {}

        categories = ["ALL", "PHYSICAL", "DIGITAL", "DIRECT", "TESTIMONIAL", "CIRCUMSTANTIAL"]
        for cat in categories:
            btn = QPushButton(cat)
            btn.setProperty("class", "btn-nav")
            btn.clicked.connect(lambda checked=False, c=cat: self._on_filter_changed(c))
            self.filter_buttons[cat] = btn
            filter_bar.addWidget(btn)

        filter_bar.addStretch(1)
        main_layout.addLayout(filter_bar)

        # Main Splitter
        splitter = QSplitter(Qt.Horizontal)

        # Left Evidence List
        left_frame = QFrame()
        left_frame.setProperty("class", "court-panel")
        l_layout = QVBoxLayout(left_frame)
        l_layout.setContentsMargins(8, 8, 8, 8)

        lbl_list = QLabel("EVIDENCE INVENTORY:")
        lbl_list.setStyleSheet(f"font-size: 11px; font-weight: bold; color: {HEX_GOLD};")
        l_layout.addWidget(lbl_list)

        self.evidence_list = QListWidget()
        self.evidence_list.currentRowChanged.connect(self._on_evidence_row_changed)
        l_layout.addWidget(self.evidence_list, 1)
        splitter.addWidget(left_frame)

        # Right Analysis Card
        right_panel = QFrame()
        right_panel.setProperty("class", "court-card-gold")
        right_panel.setStyleSheet("background-color: #241710; border: 1px solid #ffd741; border-radius: 8px; padding: 14px;")
        r_layout = QVBoxLayout(right_panel)
        r_layout.setSpacing(10)

        self.lbl_ev_name = QLabel("SELECT AN EVIDENCE ITEM")
        self.lbl_ev_name.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {HEX_GOLD};")
        r_layout.addWidget(self.lbl_ev_name)

        self.lbl_ev_meta = QLabel("Category: —  |  Reliability: —  |  Relevance: —")
        self.lbl_ev_meta.setStyleSheet(f"font-size: 12px; font-weight: bold; color: {HEX_ACCENT_BLUE};")
        r_layout.addWidget(self.lbl_ev_meta)

        self.txt_details = QTextBrowser()
        self.txt_details.setStyleSheet("background-color: #19100c; border: 1px solid #5a351c; border-radius: 6px; padding: 12px; font-size: 13px; line-height: 1.6;")
        r_layout.addWidget(self.txt_details, 1)

        splitter.addWidget(right_panel)
        splitter.setSizes([380, 720])
        main_layout.addWidget(splitter, 1)

    def on_enter_screen(self):
        self._refresh_list()

    def _on_filter_changed(self, cat: str):
        self.active_category = cat
        self.sound_service.play("click")
        self._refresh_list()

    def _refresh_list(self):
        for c, btn in self.filter_buttons.items():
            if c == self.active_category:
                btn.setStyleSheet(f"background-color: #965f23; border: 1px solid {HEX_GOLD}; color: #ffffff;")
            else:
                btn.setStyleSheet("background-color: #291a13; border: 1px solid #633c22; color: #d8c8b8;")

        self.evidence_list.clear()
        case = self.game_state.current_case
        if not case:
            return

        for ev in case.evidence_list:
            if self.active_category != "ALL" and ev.category.upper() != self.active_category:
                continue

            is_col = self.game_state.is_evidence_collected(ev.id)
            status_tag = "[COLLECTED ✓]" if is_col else "[AT SCENE]"
            item = QListWidgetItem(f"📦 {ev.name} ({ev.category.capitalize()})\n   Status: {status_tag}  |  Rel: {int(ev.reliability * 100)}%")
            item.setData(Qt.UserRole, ev)
            self.evidence_list.addItem(item)

        if self.evidence_list.count() > 0:
            self.evidence_list.setCurrentRow(0)

    def _on_evidence_row_changed(self, row: int):
        if row >= 0:
            item = self.evidence_list.item(row)
            if item:
                ev = item.data(Qt.UserRole)
                if ev:
                    self.selected_evidence = ev
                    self._update_display(ev)

    def _update_display(self, ev: Evidence):
        self.lbl_ev_name.setText(ev.name.upper())
        is_col = self.game_state.is_evidence_collected(ev.id)
        status_txt = "<span style='color: #2db955;'>COLLECTED IN LEGAL INVENTORY ✓</span>" if is_col else "<span style='color: #eb3732;'>UNCOLLECTED AT SCENE</span>"

        self.lbl_ev_meta.setText(f"Category: {ev.category.capitalize()} Evidence  |  Reliability: {int(ev.reliability * 100)}%  |  Relevance: {int(ev.relevance * 100)}%")

        html = f"""
        <p><b>Legal Custody Status:</b> {status_txt}</p>
        <p><b>Associated Suspect:</b> {ev.associated_suspect or 'None directly established'}</p>
        <hr style='border: 1px solid #704222;'>
        <h4 style='color: #ffd741; margin-top: 0;'>Forensic Description:</h4>
        <p style='color: #f5ebd7; font-size: 13px; line-height: 1.6;'>{ev.description}</p>
        <h4 style='color: #ffeb82;'>Laboratory Analysis:</h4>
        <p style='color: #d8c8b8; font-size: 13px;'>{ev.details or 'Analysis corroborates physical findings.'}</p>
        <h4 style='color: #2db955;'>Unlocked Atomic Propositions:</h4>
        <ul>
        """
        for f in ev.facts_unlocked:
            html += f"<li>{f}</li>"
        html += "</ul>"
        self.txt_details.setHtml(html)

    def _on_proceed(self):
        self.sound_service.play("click")
        self.proceed_to_board.emit()
        self.navigate.emit("case_board")

