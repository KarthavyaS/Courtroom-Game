"""Interactive 2D Crime Scene Screen for PySide6 LOGIC COURTROOM.
Integrates CrimeSceneView (QGraphicsView) with 3-tool forensic switcher and inspector panel.
"""

from typing import Optional
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QTextBrowser, QSplitter
)
from models.evidence import Evidence
from services.game_state import GameState
from services.save_service import SaveService
from app_qt.config import (
    HEX_GOLD, HEX_GOLD_LIGHT, HEX_ACCENT_GREEN, HEX_ACCENT_BLUE,
    HEX_ACCENT_RED, HEX_LIGHT_PARCHMENT, HEX_MUTED_TEXT
)
from app_qt.graphics.crime_scene_view import CrimeSceneView
from app_qt.services.sound_service_qt import get_sound_service_qt


class CrimeSceneScreenQt(QWidget):
    """Crime scene investigation screen with 2D interactive canvas and forensic inspector."""

    navigate = Signal(str)
    notify = Signal(str, str)
    proceed_to_suspects = Signal()
    notification_triggered = Signal(str, str)

    def __init__(self, game_state: GameState, save_service: SaveService, parent=None):
        super().__init__(parent)
        self.game_state = game_state
        self.save_service = save_service
        self.sound_service = get_sound_service_qt()
        self.selected_evidence: Optional[Evidence] = None

        self._build_ui()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 12, 25, 12)
        main_layout.setSpacing(10)

        # 1. Top Controls Bar (Location, Tools, Stats & Proceed)
        top_bar = QHBoxLayout()
        top_bar.setSpacing(10)

        # Location & Stats
        loc_box = QVBoxLayout()
        loc_box.setSpacing(2)
        self.lbl_location = QLabel("LOCATION: VANCE MANOR STUDY")
        self.lbl_location.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {HEX_GOLD};")
        loc_box.addWidget(self.lbl_location)

        self.lbl_stats = QLabel("Inspected: 0/0  •  Collected: 0/0")
        self.lbl_stats.setStyleSheet(f"font-size: 11px; color: {HEX_LIGHT_PARCHMENT};")
        loc_box.addWidget(self.lbl_stats)
        top_bar.addLayout(loc_box)

        top_bar.addStretch(1)

        # Forensic Tool Buttons
        self.btn_tool_lens = QPushButton("🔍 LENS [1]")
        self.btn_tool_lens.clicked.connect(lambda: self._select_tool("MAGNIFIER"))
        top_bar.addWidget(self.btn_tool_lens)

        self.btn_tool_uv = QPushButton("💡 UV LIGHT [2]")
        self.btn_tool_uv.clicked.connect(lambda: self._select_tool("LUMINOL"))
        top_bar.addWidget(self.btn_tool_uv)

        self.btn_tool_powder = QPushButton("🖌 DUST POWDER [3]")
        self.btn_tool_powder.clicked.connect(lambda: self._select_tool("POWDER"))
        top_bar.addWidget(self.btn_tool_powder)

        top_bar.addStretch(1)

        # Proceed Button
        btn_proceed = QPushButton("SUSPECTS ➔")
        btn_proceed.setProperty("class", "btn-gold")
        btn_proceed.setFixedHeight(34)
        btn_proceed.clicked.connect(self._on_proceed)
        top_bar.addWidget(btn_proceed)

        main_layout.addLayout(top_bar)

        # 2. Main Content Splitter: Left 2D Scene Canvas, Right Forensic Inspector
        splitter = QSplitter(Qt.Horizontal)

        # Left Canvas View
        self.scene_view = CrimeSceneView()
        self.scene_view.evidence_clicked.connect(self._on_evidence_clicked)
        self.scene_view.evidence_double_clicked.connect(self._on_evidence_double_clicked)
        splitter.addWidget(self.scene_view)

        # Right Inspector Panel
        inspector_frame = QFrame()
        inspector_frame.setProperty("class", "court-card-gold")
        inspector_frame.setStyleSheet("background-color: #241610; border: 1px solid #ffd741; border-radius: 8px; padding: 12px;")
        i_layout = QVBoxLayout(inspector_frame)
        i_layout.setSpacing(10)

        self.lbl_insp_title = QLabel("EVIDENCE INSPECTOR")
        self.lbl_insp_title.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {HEX_GOLD};")
        i_layout.addWidget(self.lbl_insp_title)

        self.lbl_insp_status = QLabel("[SELECT AN ARTIFACT IN ROOM]")
        self.lbl_insp_status.setStyleSheet("font-size: 11px; font-weight: bold; color: #b8a896;")
        i_layout.addWidget(self.lbl_insp_status)

        self.lbl_insp_metrics = QLabel("Reliability: —  •  Relevance: —")
        self.lbl_insp_metrics.setStyleSheet(f"font-size: 11px; font-weight: bold; color: {HEX_ACCENT_BLUE};")
        i_layout.addWidget(self.lbl_insp_metrics)

        self.txt_insp_details = QTextBrowser()
        self.txt_insp_details.setStyleSheet("background-color: #19100c; border: 1px solid #5a351c; border-radius: 6px; padding: 10px; font-size: 12px; line-height: 1.5;")
        i_layout.addWidget(self.txt_insp_details, 1)

        # Action Buttons
        btn_box = QHBoxLayout()
        self.btn_inspect = QPushButton("INSPECT 🔍")
        self.btn_inspect.setStyleSheet("background-color: #3d2b20; border: 1px solid #8c5a2e; padding: 8px;")
        self.btn_inspect.clicked.connect(self._inspect_current_evidence)
        btn_box.addWidget(self.btn_inspect)

        self.btn_collect = QPushButton("COLLECT CLUE ➔")
        self.btn_collect.setProperty("class", "btn-success")
        self.btn_collect.setStyleSheet("padding: 8px;")
        self.btn_collect.clicked.connect(self._collect_current_evidence)
        btn_box.addWidget(self.btn_collect)
        i_layout.addLayout(btn_box)

        splitter.addWidget(inspector_frame)
        splitter.setSizes([710, 350])
        main_layout.addWidget(splitter, 1)

        self._select_tool("MAGNIFIER")

    def on_enter_screen(self):
        case = self.game_state.current_case
        if not case:
            return

        self.lbl_location.setText(f"LOCATION: {case.scene_name.upper()} ({case.scene_type.upper()})")
        self._refresh_stats()
        self.scene_view.set_case(case, self.game_state.collected_evidence_ids, self.game_state.progress.inspected_evidence_ids, self.selected_evidence)

        if case.evidence_list:
            # Default select first clue
            self._on_evidence_clicked(case.evidence_list[0])

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_1:
            self._select_tool("MAGNIFIER")
        elif event.key() == Qt.Key_2:
            self._select_tool("LUMINOL")
        elif event.key() == Qt.Key_3:
            self._select_tool("POWDER")
        super().keyPressEvent(event)

    def _select_tool(self, tool_name: str):
        self.scene_view.set_tool(tool_name)
        active_style = f"background-color: #965f23; border: 1px solid {HEX_GOLD}; color: #ffffff; font-weight: bold;"
        inactive_style = "background-color: #291a13; border: 1px solid #633c22; color: #d8c8b8;"

        self.btn_tool_lens.setStyleSheet(active_style if tool_name == "MAGNIFIER" else inactive_style)
        self.btn_tool_uv.setStyleSheet(active_style if tool_name == "LUMINOL" else inactive_style)
        self.btn_tool_powder.setStyleSheet(active_style if tool_name == "POWDER" else inactive_style)

        self.sound_service.play("click")
        if tool_name == "LUMINOL":
            self.notification_triggered.emit("UV Luminol Light Active: Latent organic & blood traces now luminesce!", "INFO")
        elif tool_name == "POWDER":
            self.notification_triggered.emit("Fingerprint Dust Powder Active: Ridge patterns highlighted!", "INFO")
        else:
            self.notification_triggered.emit("Forensic Magnifying Lens Active: Standard optical inspection.", "INFO")

    def _on_evidence_clicked(self, evidence: Evidence):
        self.selected_evidence = evidence
        self.game_state.progress.record_evidence_inspected(evidence.id)
        self.save_service.save_active_game(self.game_state)
        self._refresh_stats()
        self._update_inspector_display(evidence)

    def _on_evidence_double_clicked(self, evidence: Evidence):
        self._on_evidence_clicked(evidence)
        self._collect_current_evidence()

    def _inspect_current_evidence(self):
        if self.selected_evidence:
            self.sound_service.play("click")
            self.game_state.progress.record_evidence_inspected(self.selected_evidence.id)
            self.save_service.save_active_game(self.game_state)
            self._refresh_stats()
            self._update_inspector_display(self.selected_evidence)
            self.notification_triggered.emit(f"Inspected '{self.selected_evidence.name}'.", "INFO")

    def _collect_current_evidence(self):
        if not self.selected_evidence:
            return

        ev_id = self.selected_evidence.id
        if self.game_state.is_evidence_collected(ev_id):
            self.notification_triggered.emit("Evidence already collected in legal inventory.", "INFO")
            return

        self.game_state.collect_evidence(ev_id)
        self.sound_service.play("evidence")
        self.save_service.save_active_game(self.game_state)
        self._refresh_stats()
        self.scene_view.set_case(self.game_state.current_case, self.game_state.collected_evidence_ids, self.game_state.progress.inspected_evidence_ids, self.selected_evidence)
        self._update_inspector_display(self.selected_evidence)
        self.notification_triggered.emit(f"Collected: '{self.selected_evidence.name}'!", "SUCCESS")

    def _update_inspector_display(self, ev: Evidence):
        self.lbl_insp_title.setText(ev.name.upper())
        is_col = self.game_state.is_evidence_collected(ev.id)

        if is_col:
            self.lbl_insp_status.setText("[COLLECTED IN LEGAL INVENTORY ✓]")
            self.lbl_insp_status.setStyleSheet(f"font-size: 11px; font-weight: bold; color: {HEX_ACCENT_GREEN};")
            self.btn_collect.setEnabled(False)
            self.btn_collect.setText("ALREADY COLLECTED ✓")
        else:
            self.lbl_insp_status.setText("[UNCOLLECTED ARTIFACT AT SCENE]")
            self.lbl_insp_status.setStyleSheet("font-size: 11px; font-weight: bold; color: #e6a840;")
            self.btn_collect.setEnabled(True)
            self.btn_collect.setText("COLLECT CLUE ➔")

        self.lbl_insp_metrics.setText(f"Category: {ev.category.capitalize()}  |  Reliability: {int(ev.reliability * 100)}%  |  Relevance: {int(ev.relevance * 100)}%")

        html = f"""
        <h4 style='color: #ffd741; margin-top: 0;'>Field Observation:</h4>
        <p style='color: #f5ebd7; font-size: 12px; line-height: 1.5;'>{ev.description}</p>
        <hr style='border: 1px solid #704222;'>
        <h4 style='color: #ffeb82;'>Forensic Lab Analysis:</h4>
        <p style='color: #d8c8b8; font-size: 12px;'>{ev.details or 'Analysis corroborates physical findings.'}</p>
        <h4 style='color: #2db955;'>Unlocked Logical Propositions:</h4>
        <ul style='color: #f5ebd7; font-size: 12px;'>
        """
        for f in ev.facts_unlocked:
            html += f"<li>{f}</li>"
        html += "</ul>"
        self.txt_insp_details.setHtml(html)

    def _refresh_stats(self):
        case = self.game_state.current_case
        if case:
            tot = len(case.evidence_list)
            insp = len(self.game_state.progress.inspected_evidence_ids)
            col = len(self.game_state.collected_evidence_ids)
            self.lbl_stats.setText(f"Inspected: {insp}/{tot}  •  Collected: {col}/{tot}")

    def _on_proceed(self):
        self.sound_service.play("click")
        if len(self.game_state.collected_evidence_ids) == 0:
            self.notification_triggered.emit("Warning: You have not collected any physical evidence yet!", "WARNING")
            self.notify.emit("WARNING", "You have not collected any physical evidence yet!")
        self.proceed_to_suspects.emit()
        self.navigate.emit("suspects")

