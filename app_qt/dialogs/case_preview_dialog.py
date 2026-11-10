"""Modal Case Preview Dialog for PySide6 LOGIC COURTROOM.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextBrowser, QFrame
)
from models.case import Case
from app_qt.config import (
    HEX_GOLD, HEX_GOLD_LIGHT, HEX_BG_PANEL, HEX_ACCENT_GREEN,
    HEX_LIGHT_PARCHMENT
)


class CasePreviewDialogQt(QDialog):
    """Case dossier preview card shown before starting an investigation."""

    def __init__(self, case: Case, parent=None):
        super().__init__(parent)
        self.case = case
        self.setWindowTitle(case.title)
        self.setModal(True)
        self.setFixedSize(650, 480)
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        card = QFrame(self)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: #241610;
                border: 2px solid {HEX_GOLD};
                border-radius: 12px;
            }}
        """)
        c_layout = QVBoxLayout(card)
        c_layout.setContentsMargins(24, 20, 24, 20)
        c_layout.setSpacing(14)

        # Header Title
        lbl_title = QLabel(case.title.upper())
        lbl_title.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {HEX_GOLD}; border: none;")
        c_layout.addWidget(lbl_title)

        # Meta pills
        meta_txt = f"Category: {case.type.upper()}  |  Scene: {case.scene_name}  |  Difficulty: {case.difficulty.upper()}  |  Reward: {case.reward} XP"
        lbl_meta = QLabel(meta_txt)
        lbl_meta.setStyleSheet(f"font-size: 11px; font-weight: bold; color: {HEX_GOLD_LIGHT}; border: none;")
        c_layout.addWidget(lbl_meta)

        # HTML Dossier Viewer
        browser = QTextBrowser()
        browser.setStyleSheet("background-color: #19100c; border: 1px solid #55331e; border-radius: 6px; padding: 10px;")

        html = f"""
        <h3 style='color: #ffd741; margin-top: 0;'>Incident Synopsis:</h3>
        <p style='color: #f5ebd7; font-size: 13px; line-height: 1.6;'>{case.description}</p>
        <hr style='border: 1px solid #704222;'>
        <h4 style='color: #ffeb82;'>Suspects Indicted ({len(case.suspects)}):</h4>
        <ul style='color: #f5ebd7; font-size: 12px;'>
        """
        for s in case.suspects:
            html += f"<li><b>{s.name}</b> — {s.occupation} ({s.relationship})</li>"
        html += f"""
        </ul>
        <h4 style='color: #ffeb82;'>Initial Verified Facts ({len(case.initial_facts)}):</h4>
        <ul style='color: #d8c8b8; font-size: 12px;'>
        """
        for f in case.initial_facts:
            html += f"<li>{f}</li>"
        html += "</ul>"

        browser.setHtml(html)
        c_layout.addWidget(browser, 1)

        # Buttons
        btn_box = QHBoxLayout()
        btn_box.setSpacing(14)

        btn_cancel = QPushButton("← BACK TO DOCKET")
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #423026;
                border: 1px solid #70523e;
                padding: 9px 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5c4234;
            }
        """)
        btn_cancel.clicked.connect(self.reject)
        btn_box.addWidget(btn_cancel)

        btn_start = QPushButton("COMMENCE INVESTIGATION ➔")
        btn_start.setStyleSheet(f"""
            QPushButton {{
                background-color: #24883d;
                border: 1px solid {HEX_ACCENT_GREEN};
                padding: 9px 18px;
                font-weight: bold;
                color: #ffffff;
            }}
            QPushButton:hover {{
                background-color: #2ea043;
            }}
        """)
        btn_start.clicked.connect(self.accept)
        btn_box.addWidget(btn_start)

        c_layout.addLayout(btn_box)
        layout.addWidget(card)

