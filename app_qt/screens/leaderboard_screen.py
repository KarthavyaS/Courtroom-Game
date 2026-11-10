"""Leaderboard & Records Screen for PySide6 LOGIC COURTROOM.
Displays persistent barrister rankings, verdict honors, and deductive test scores.
"""

from typing import Optional, List, Dict, Any
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QTableWidget, QTableWidgetItem, QHeaderView, QSizePolicy
)

from services.save_service import SaveService
from app_qt.config import (
    COLOR_BG_CARD, COLOR_BG_PANEL, COLOR_BORDER, COLOR_GOLD, COLOR_GOLD_LIGHT,
    COLOR_WHITE, COLOR_TEXT_MUTED, COLOR_TEXT_PARCHMENT, COLOR_ACCENT_GREEN,
    COLOR_ACCENT_RED, COLOR_ACCENT_BLUE, get_qt_font
)
from app_qt.services.sound_service_qt import get_sound_service_qt


class LeaderboardScreenQt(QWidget):
    """Courtroom Barrister Roll of Honor leaderboard screen."""

    navigate = Signal(str)
    notify = Signal(str, str)

    def __init__(self, save_service: Optional[SaveService] = None, parent=None):
        super().__init__(parent)
        self.save_service = save_service or SaveService()
        self.sound_service = get_sound_service_qt()

        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 16, 24, 16)
        main_layout.setSpacing(14)

        # 1. Header Bar
        header_layout = QHBoxLayout()

        btn_back = QPushButton("← HUB")
        btn_back.setFont(get_qt_font(10, bold=True))
        btn_back.setStyleSheet("padding: 7px 16px; background-color: #2b1f14; color: #c9a050; border: 1px solid #5a381e; border-radius: 4px;")
        btn_back.clicked.connect(lambda: self.navigate.emit("dashboard"))
        header_layout.addWidget(btn_back)

        title_lbl = QLabel("HALL OF FAME • COURT OF RECORD")
        title_lbl.setFont(get_qt_font(16, bold=True))
        title_lbl.setStyleSheet(f"color: {COLOR_GOLD.name()}; margin-left: 12px; letter-spacing: 1px;")
        header_layout.addWidget(title_lbl)

        header_layout.addStretch()

        btn_refresh = QPushButton("REFRESH ↺")
        btn_refresh.setFont(get_qt_font(10, bold=True))
        btn_refresh.setStyleSheet("padding: 7px 16px; background-color: #1e3a5f; color: #fff; border: 1px solid #3a75b4; border-radius: 4px;")
        btn_refresh.clicked.connect(self.refresh_records)
        header_layout.addWidget(btn_refresh)

        main_layout.addLayout(header_layout)

        # 2. Table Widget
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["RANK", "ADVOCATE", "CASE TITLE", "VERDICT", "SCORE", "DATE FILED"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {COLOR_BG_CARD.name()};
                border: 1px solid {COLOR_BORDER.name()};
                border-radius: 8px;
                gridline-color: #2b1f14;
                color: #e6d3a3;
                selection-background-color: #4a3424;
            }}
            QHeaderView::section {{
                background-color: #211713;
                color: {COLOR_GOLD.name()};
                padding: 10px;
                border: 1px solid #3d2b1f;
                font-weight: bold;
            }}
            QTableWidget::item {{
                padding: 8px;
            }}
        """)
        main_layout.addWidget(self.table, stretch=1)

    def refresh_records(self):
        records = self.save_service.get_leaderboard()
        self.table.setRowCount(len(records))

        for row, rec in enumerate(records):
            # Rank
            rank_str = f"#{row + 1}"
            rank_item = QTableWidgetItem(rank_str)
            rank_item.setTextAlignment(Qt.AlignCenter)
            if row == 0:
                rank_item.setForeground(COLOR_GOLD)
            elif row == 1:
                rank_item.setForeground(COLOR_GOLD_LIGHT)
            elif row == 2:
                rank_item.setForeground(COLOR_WHITE)
            else:
                rank_item.setForeground(COLOR_TEXT_MUTED)
            self.table.setItem(row, 0, rank_item)

            # Advocate
            adv_item = QTableWidgetItem(str(rec.get("player_name", "Anonymous")))
            adv_item.setForeground(COLOR_WHITE)
            self.table.setItem(row, 1, adv_item)

            # Case Title
            case_item = QTableWidgetItem(str(rec.get("case_title", "Unknown Case")))
            case_item.setForeground(COLOR_TEXT_PARCHMENT)
            self.table.setItem(row, 2, case_item)

            # Verdict
            verdict = rec.get("verdict", "INCONCLUSIVE")
            v_item = QTableWidgetItem(verdict)
            v_item.setTextAlignment(Qt.AlignCenter)
            if verdict == "SUPPORTED":
                v_item.setForeground(COLOR_ACCENT_GREEN)
            else:
                v_item.setForeground(COLOR_GOLD)
            self.table.setItem(row, 3, v_item)

            # Score
            score_txt = f"{rec.get('score', 0)} PTS"
            score_item = QTableWidgetItem(score_txt)
            score_item.setTextAlignment(Qt.AlignCenter)
            score_item.setForeground(COLOR_GOLD_LIGHT)
            self.table.setItem(row, 4, score_item)

            # Date
            d_str = str(rec.get("date", rec.get("timestamp", "")))[:16]
            date_item = QTableWidgetItem(d_str)
            date_item.setForeground(COLOR_TEXT_MUTED)
            self.table.setItem(row, 5, date_item)

    def on_enter_screen(self):
        self.refresh_records()

