"""Case Board Screen for PySide6 LOGIC COURTROOM.
Visualizes suspects, physical evidence, and forensic contradictions on an interactive corkboard
with draggable parchment pins, connected yarn links, and a 24-hour timeline scrubber.
"""

from typing import Optional, List, Dict
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QSizePolicy
)

from services.game_state import GameState
from services.save_service import SaveService
from app_qt.config import (
    COLOR_BG_CARD, COLOR_BORDER, COLOR_GOLD, COLOR_GOLD_LIGHT,
    COLOR_WHITE, COLOR_TEXT_MUTED, COLOR_ACCENT_RED, COLOR_ACCENT_GREEN,
    get_qt_font
)
from app_qt.graphics.corkboard_view import CorkboardView
from app_qt.graphics.corkboard_items import CorkNodeItem
from app_qt.services.sound_service_qt import get_sound_service_qt


class CaseBoardScreenQt(QWidget):
    """Interactive corkboard detective deduction screen."""

    navigate = Signal(str)
    notify = Signal(str, str)

    def __init__(self, game_state: GameState, save_service: Optional[SaveService] = None, parent=None):
        super().__init__(parent)
        self.game_state = game_state
        self.save_service = save_service or SaveService()
        self.sound_service = get_sound_service_qt()

        self.time_slots = [
            {"time": "09:30 PM", "label": "Arrival", "desc": "Lord Blackwood seen entering study. Household retired."},
            {"time": "10:15 PM", "label": "Dinner Alibi", "desc": "Suspects claim dinner concluded. Servants cleared hall."},
            {"time": "11:00 PM", "label": "★ CRIME WINDOW", "desc": "Loud struggle heard. Safe alarms bypassed via Master Cipher."},
            {"time": "11:20 PM", "label": "Escape / CCTV", "desc": "Dark sedan filmed departing north gate without headlights."},
            {"time": "12:00 AM", "label": "Discovery", "desc": "Butler discovered open safe and alerted Scotland Yard."}
        ]
        self.selected_time_idx = 2
        self.timeline_buttons: List[QPushButton] = []

        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 16, 24, 16)
        main_layout.setSpacing(12)

        # 1. Top Header & Filter Controls
        header_layout = QHBoxLayout()

        title_col = QVBoxLayout()
        title_col.setSpacing(2)
        title_lbl = QLabel("CASE EVIDENCE BOARD")
        title_lbl.setFont(get_qt_font(18, bold=True))
        title_lbl.setStyleSheet(f"color: {COLOR_GOLD.name()}; letter-spacing: 1px;")

        sub_lbl = QLabel("Connect physical evidence, witness alibis, and timeline anomalies via forensic yarn.")
        sub_lbl.setFont(get_qt_font(10))
        sub_lbl.setStyleSheet(f"color: {COLOR_TEXT_MUTED.name()};")
        title_col.addWidget(title_lbl)
        title_col.addWidget(sub_lbl)
        header_layout.addLayout(title_col)

        header_layout.addStretch()

        # Filter Buttons
        self.btn_filter_all = QPushButton("ALL LINKS")
        self.btn_filter_all.setFont(get_qt_font(10, bold=True))
        self.btn_filter_all.setStyleSheet("padding: 6px 14px; background-color: #5a381e; color: #fff; border: 1px solid #c9a050; border-radius: 4px;")
        self.btn_filter_all.clicked.connect(lambda: self._set_filter("ALL"))
        header_layout.addWidget(self.btn_filter_all)

        self.btn_filter_conf = QPushButton("CONFIRMED LINKS")
        self.btn_filter_conf.setFont(get_qt_font(10, bold=True))
        self.btn_filter_conf.setStyleSheet("padding: 6px 14px; background-color: #2b3a2b; color: #e0d0b0; border: 1px solid #4a6a4a; border-radius: 4px;")
        self.btn_filter_conf.clicked.connect(lambda: self._set_filter("CONFIRMED"))
        header_layout.addWidget(self.btn_filter_conf)

        self.btn_filter_cont = QPushButton("CONTRADICTIONS ⚡")
        self.btn_filter_cont.setFont(get_qt_font(10, bold=True))
        self.btn_filter_cont.setStyleSheet("padding: 6px 14px; background-color: #4a2222; color: #ff8888; border: 1px solid #883333; border-radius: 4px;")
        self.btn_filter_cont.clicked.connect(lambda: self._set_filter("CONTRADICTIONS"))
        header_layout.addWidget(self.btn_filter_cont)

        # Proceed button
        self.btn_proceed = QPushButton("PREPARE ARGUMENTS ➔")
        self.btn_proceed.setFont(get_qt_font(11, bold=True))
        self.btn_proceed.setStyleSheet("padding: 8px 18px; background-color: #8b2500; color: #fff; border: 1px solid #d4af37; border-radius: 4px;")
        self.btn_proceed.clicked.connect(self._on_proceed_clicked)
        header_layout.addWidget(self.btn_proceed)

        main_layout.addLayout(header_layout)

        # 2. Main Center Body: Corkboard Canvas (Left) + Node Inspector (Right)
        body_layout = QHBoxLayout()
        body_layout.setSpacing(12)

        self.corkboard_view = CorkboardView(self)
        self.corkboard_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.corkboard_view.node_selected.connect(self._on_node_selected)
        body_layout.addWidget(self.corkboard_view, stretch=4)

        # Inspector Card
        self.inspector_frame = QFrame()
        self.inspector_frame.setFixedWidth(240)
        self.inspector_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLOR_BG_CARD.name()};
                border: 1px solid {COLOR_BORDER.name()};
                border-radius: 8px;
            }}
        """)
        insp_layout = QVBoxLayout(self.inspector_frame)
        insp_layout.setContentsMargins(14, 14, 14, 14)
        insp_layout.setSpacing(8)

        insp_header = QLabel("📌 PIN DETAILS")
        insp_header.setFont(get_qt_font(11, bold=True))
        insp_header.setStyleSheet(f"color: {COLOR_GOLD.name()}; border-bottom: 1px solid #3d2c1e; padding-bottom: 4px;")
        insp_layout.addWidget(insp_header)

        self.lbl_node_title = QLabel("Select any pin on the corkboard to inspect evidence connections.")
        self.lbl_node_title.setFont(get_qt_font(11, bold=True))
        self.lbl_node_title.setWordWrap(True)
        self.lbl_node_title.setStyleSheet("color: #e6d3a3;")
        insp_layout.addWidget(self.lbl_node_title)

        self.lbl_node_type = QLabel("")
        self.lbl_node_type.setFont(get_qt_font(9, bold=True))
        self.lbl_node_type.setStyleSheet("color: #c9a050;")
        insp_layout.addWidget(self.lbl_node_type)

        self.lbl_node_desc = QLabel("")
        self.lbl_node_desc.setFont(get_qt_font(9))
        self.lbl_node_desc.setWordWrap(True)
        self.lbl_node_desc.setStyleSheet(f"color: {COLOR_TEXT_MUTED.name()};")
        insp_layout.addWidget(self.lbl_node_desc)

        insp_layout.addStretch()

        help_hint = QLabel("💡 Tip: Drag pins to rearrange your detective mind map. Yarn links update dynamically.")
        help_hint.setFont(get_qt_font(8, italic=True))
        help_hint.setWordWrap(True)
        help_hint.setStyleSheet("color: #8c7355; border-top: 1px dashed #3d2c1e; padding-top: 6px;")
        insp_layout.addWidget(help_hint)

        body_layout.addWidget(self.inspector_frame, stretch=1)
        main_layout.addLayout(body_layout, stretch=1)

        # 3. Bottom 24-Hour Timeline Scrubber Area
        timeline_container = QFrame()
        timeline_container.setStyleSheet(f"""
            QFrame {{
                background-color: #17110e;
                border: 1px solid {COLOR_BORDER.name()};
                border-radius: 8px;
            }}
        """)
        timeline_layout = QVBoxLayout(timeline_container)
        timeline_layout.setContentsMargins(12, 8, 12, 10)
        timeline_layout.setSpacing(6)

        t_header = QLabel("⏱ 24-HOUR FORENSIC TIMELINE SCRUBBER (CLICK EVENT TO JUMP)")
        t_header.setFont(get_qt_font(9, bold=True))
        t_header.setStyleSheet(f"color: {COLOR_GOLD.name()};")
        timeline_layout.addWidget(t_header)

        slots_layout = QHBoxLayout()
        slots_layout.setSpacing(8)

        for idx, slot in enumerate(self.time_slots):
            btn = QPushButton()
            btn.setCheckable(True)
            btn.setChecked(idx == self.selected_time_idx)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            btn.setMinimumHeight(54)
            btn.clicked.connect(lambda checked=False, i=idx: self._select_timeline_slot(i))

            # HTML text formatting inside slot button
            label_col = "#ff5555" if "CRIME" in slot["label"] else "#e6d3a3"
            btn_text = f"<b>{slot['time']}</b> - <span style='color:{label_col}; font-weight:bold;'>{slot['label']}</span><br><span style='font-size:11px; color:#9c8570;'>{slot['desc']}</span>"
            btn.setText(slot["time"] + " - " + slot["label"] + "\n" + slot["desc"])
            btn.setStyleSheet(self._get_slot_style(idx == self.selected_time_idx))

            self.timeline_buttons.append(btn)
            slots_layout.addWidget(btn)

        timeline_layout.addLayout(slots_layout)
        main_layout.addWidget(timeline_container)

    def _get_slot_style(self, active: bool) -> str:
        if active:
            return """
                QPushButton {
                    background-color: #3d2b1f;
                    border: 2px solid #d4af37;
                    border-radius: 6px;
                    color: #fff;
                    text-align: left;
                    padding: 6px;
                }
            """
        else:
            return """
                QPushButton {
                    background-color: #211713;
                    border: 1px solid #3d2b1f;
                    border-radius: 6px;
                    color: #c0b090;
                    text-align: left;
                    padding: 6px;
                }
                QPushButton:hover {
                    background-color: #2c1f19;
                    border-color: #8c6d48;
                }
            """

    def _select_timeline_slot(self, idx: int):
        self.selected_time_idx = idx
        self.sound_service.play("click")
        for i, b in enumerate(self.timeline_buttons):
            b.setChecked(i == idx)
            b.setStyleSheet(self._get_slot_style(i == idx))

        slot = self.time_slots[idx]
        self.lbl_node_title.setText(f"Timeline: {slot['time']} - {slot['label']}")
        self.lbl_node_type.setText("CATEGORY: TIMELINE EVENT")
        self.lbl_node_desc.setText(slot["desc"])

    def _set_filter(self, mode: str):
        self.sound_service.play("click")
        self.corkboard_view.set_filter(mode)

        # Style active filter
        self.btn_filter_all.setStyleSheet("padding: 6px 14px; background-color: #5a381e; color: #fff; border: 1px solid #c9a050; border-radius: 4px;" if mode == "ALL" else "padding: 6px 14px; background-color: #211713; color: #9c8570; border: 1px solid #3d2b1f; border-radius: 4px;")
        self.btn_filter_conf.setStyleSheet("padding: 6px 14px; background-color: #2b3a2b; color: #e0d0b0; border: 1px solid #4a6a4a; border-radius: 4px;" if mode == "CONFIRMED" else "padding: 6px 14px; background-color: #211713; color: #9c8570; border: 1px solid #3d2b1f; border-radius: 4px;")
        self.btn_filter_cont.setStyleSheet("padding: 6px 14px; background-color: #4a2222; color: #ff8888; border: 1px solid #883333; border-radius: 4px;" if mode == "CONTRADICTIONS" else "padding: 6px 14px; background-color: #211713; color: #9c8570; border: 1px solid #3d2b1f; border-radius: 4px;")

    def _on_node_selected(self, item: CorkNodeItem):
        self.sound_service.play("click")
        self.lbl_node_title.setText(item.title.replace("\n", " "))
        self.lbl_node_type.setText(f"CATEGORY: {item.category.upper()}")

        case = self.game_state.current_case
        desc = "Active pin on detective deduction board."

        if item.category == "suspect" and case:
            suspect = next((s for s in case.suspects if s.id == item.node_id), None)
            if suspect:
                desc = f"Occupation: {suspect.occupation}\nMotive: {suspect.motive}\nAlibi: {suspect.alibi}"
        elif item.category == "evidence" and case:
            ev = next((e for e in case.evidence_list if e.id == item.node_id), None)
            if ev:
                desc = f"Reliability: {int(ev.reliability * 100)}%\nRelevance: {int(ev.relevance * 100)}%\nUnlocked Facts:\n- " + "\n- ".join(ev.unlocked_facts or ["None"])
        elif item.category == "contradiction":
            desc = "Physical evidence contradicts testimony! Can be leveraged in the courtroom during cross-examination."

        self.lbl_node_desc.setText(desc)

    def _on_proceed_clicked(self):
        self.sound_service.play("click")
        self.navigate.emit("arguments")

    def on_enter_screen(self):
        """Called when this screen becomes active."""
        self.game_state.progress.record_case_board_opened()
        self.save_service.save_active_game(self.game_state)
        self.corkboard_view.set_case(self.game_state.current_case)

