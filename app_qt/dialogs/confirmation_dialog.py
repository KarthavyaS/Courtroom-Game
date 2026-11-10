"""Modal Confirmation Dialog for PySide6 LOGIC COURTROOM.
"""

from typing import Optional
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
)
from app_qt.config import (
    HEX_GOLD, HEX_GOLD_LIGHT, HEX_BG_PANEL, HEX_ACCENT_RED,
    HEX_LIGHT_PARCHMENT
)


class ConfirmationDialogQt(QDialog):
    """Modal confirmation prompt styled with Victorian dark aesthetics."""

    def __init__(
        self,
        title: str,
        message: str,
        confirm_text: str = "CONFIRM",
        cancel_text: str = "CANCEL",
        is_destructive: bool = False,
        parent=None
    ):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedSize(460, 210)
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Card body
        card = QFrame(self)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: #241610;
                border: 2px solid {HEX_GOLD};
                border-radius: 10px;
            }}
        """)
        c_layout = QVBoxLayout(card)
        c_layout.setContentsMargins(24, 20, 24, 20)
        c_layout.setSpacing(14)

        # Title
        lbl_title = QLabel(title.upper())
        lbl_title.setStyleSheet(f"font-size: 15px; font-weight: bold; color: {HEX_GOLD}; border: none;")
        lbl_title.setAlignment(Qt.AlignCenter)
        c_layout.addWidget(lbl_title)

        # Message
        lbl_msg = QLabel(message)
        lbl_msg.setStyleSheet(f"font-size: 12px; color: {HEX_LIGHT_PARCHMENT}; line-height: 1.5; border: none;")
        lbl_msg.setWordWrap(True)
        lbl_msg.setAlignment(Qt.AlignCenter)
        c_layout.addWidget(lbl_msg, 1)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(14)

        btn_cancel = QPushButton(cancel_text)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #423026;
                border: 1px solid #70523e;
                padding: 8px 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5c4234;
            }
        """)
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)

        btn_confirm = QPushButton(confirm_text)
        confirm_bg = HEX_ACCENT_RED if is_destructive else "#287a3e"
        btn_confirm.setStyleSheet(f"""
            QPushButton {{
                background-color: {confirm_bg};
                border: 1px solid #ffffff;
                padding: 8px 18px;
                font-weight: bold;
                color: #ffffff;
            }}
            QPushButton:hover {{
                background-color: #d1302b if {is_destructive} else #34944d;
            }}
        """)
        btn_confirm.clicked.connect(self.accept)
        btn_layout.addWidget(btn_confirm)

        c_layout.addLayout(btn_layout)
        layout.addWidget(card)

