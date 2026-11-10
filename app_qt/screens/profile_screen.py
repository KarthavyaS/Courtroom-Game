"""Player Profile & Career Statistics Screen for PySide6 LOGIC COURTROOM.
Allows players to customize their advocate name, select avatar persona,
and view career win/loss statistics, accuracy ratings, and achievements.
"""

from typing import Optional, List
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QFrame, QScrollArea, QGridLayout, QSizePolicy
)

from services.game_state import GameState
from services.save_service import SaveService
from app_qt.config import (
    COLOR_BG_CARD, COLOR_BG_PANEL, COLOR_BORDER, COLOR_GOLD, COLOR_GOLD_LIGHT,
    COLOR_GOLD_DARK, COLOR_WHITE, COLOR_TEXT_MUTED, COLOR_TEXT_PARCHMENT,
    COLOR_ACCENT_GREEN, COLOR_ACCENT_RED, COLOR_ACCENT_BLUE, get_qt_font
)
from app_qt.services.sound_service_qt import get_sound_service_qt
from app_qt.widgets.character_avatar import CharacterAvatarQt


class ProfileScreenQt(QWidget):
    """Player Profile & Career Dossier Screen."""

    navigate = Signal(str)
    notify = Signal(str, str)

    def __init__(self, game_state: GameState, save_service: Optional[SaveService] = None, parent=None):
        super().__init__(parent)
        self.game_state = game_state
        self.save_service = save_service or SaveService()
        self.sound_service = get_sound_service_qt()

        self.avatars = ["lawyer", "socialite", "butler", "doctor"]
        self.avatar_buttons: List[QPushButton] = []

        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 16, 24, 16)
        main_layout.setSpacing(12)

        # 1. Header Bar
        header_layout = QHBoxLayout()

        btn_back = QPushButton("← HUB")
        btn_back.setFont(get_qt_font(10, bold=True))
        btn_back.setStyleSheet("padding: 7px 16px; background-color: #2b1f14; color: #c9a050; border: 1px solid #5a381e; border-radius: 4px;")
        btn_back.clicked.connect(lambda: self.navigate.emit("dashboard"))
        header_layout.addWidget(btn_back)

        btn_main_menu = QPushButton("⌂ MAIN MENU")
        btn_main_menu.setFont(get_qt_font(10, bold=True))
        btn_main_menu.setStyleSheet("padding: 7px 16px; background-color: #2b1f14; color: #c9a050; border: 1px solid #5a381e; border-radius: 4px;")
        btn_main_menu.clicked.connect(lambda: self.navigate.emit("welcome"))
        header_layout.addWidget(btn_main_menu)

        title_lbl = QLabel("BARRISTER DOSSIER & PROFILE")
        title_lbl.setFont(get_qt_font(16, bold=True))
        title_lbl.setStyleSheet(f"color: {COLOR_GOLD.name()}; margin-left: 12px; letter-spacing: 1px;")
        header_layout.addWidget(title_lbl)

        header_layout.addStretch()

        btn_save = QPushButton("SAVE PROFILE 💾")
        btn_save.setFont(get_qt_font(11, bold=True))
        btn_save.setStyleSheet(f"padding: 8px 18px; background-color: {COLOR_ACCENT_GREEN.name()}; color: #fff; border: 1px solid #3d8c3d; border-radius: 4px;")
        btn_save.clicked.connect(self._save_profile)
        header_layout.addWidget(btn_save)

        main_layout.addLayout(header_layout)

        # 2. Two-Column Body
        body_layout = QHBoxLayout()
        body_layout.setSpacing(14)

        # ==========================
        # Left Column: Identity Card
        # ==========================
        left_frame = QFrame()
        left_frame.setFixedWidth(340)
        left_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLOR_BG_CARD.name()};
                border: 1px solid {COLOR_BORDER.name()};
                border-radius: 8px;
            }}
        """)
        l_layout = QVBoxLayout(left_frame)
        l_layout.setContentsMargins(18, 16, 18, 16)
        l_layout.setSpacing(10)

        id_header = QLabel("ADVOCATE IDENTITY")
        id_header.setFont(get_qt_font(11, bold=True))
        id_header.setStyleSheet(f"color: {COLOR_GOLD.name()};")
        l_layout.addWidget(id_header)

        # Avatar Preview
        self.avatar_preview = CharacterAvatarQt(
            character_type=self.game_state.profile.avatar_id or "lawyer",
            name=self.game_state.profile.name,
            parent=self
        )
        self.avatar_preview.setFixedSize(120, 110)
        l_layout.addWidget(self.avatar_preview, alignment=Qt.AlignCenter)

        # Name edit
        lbl_name = QLabel("ADVOCATE FULL NAME:")
        lbl_name.setFont(get_qt_font(9, bold=True))
        lbl_name.setStyleSheet(f"color: {COLOR_GOLD.name()};")
        l_layout.addWidget(lbl_name)

        self.txt_name = QLineEdit(self.game_state.profile.name)
        self.txt_name.setFont(get_qt_font(11))
        self.txt_name.setStyleSheet(f"""
            QLineEdit {{
                background-color: #17110e;
                color: #e6d3a3;
                border: 1px solid #3d2b1f;
                border-radius: 4px;
                padding: 6px 10px;
            }}
            QLineEdit:focus {{
                border: 1px solid {COLOR_GOLD.name()};
            }}
        """)
        l_layout.addWidget(self.txt_name)

        # Rank Badge
        lbl_rank = QLabel("OFFICIAL JUDICIAL RANK:")
        lbl_rank.setFont(get_qt_font(9, bold=True))
        lbl_rank.setStyleSheet(f"color: {COLOR_GOLD.name()};")
        l_layout.addWidget(lbl_rank)

        self.lbl_rank_badge = QLabel()
        self.lbl_rank_badge.setFont(get_qt_font(11, bold=True))
        self.lbl_rank_badge.setAlignment(Qt.AlignCenter)
        self.lbl_rank_badge.setFixedHeight(36)
        self.lbl_rank_badge.setStyleSheet(f"""
            QLabel {{
                background-color: #211713;
                border: 1px solid {COLOR_GOLD.name()};
                border-radius: 6px;
                color: {COLOR_GOLD_LIGHT.name()};
            }}
        """)
        l_layout.addWidget(self.lbl_rank_badge)

        # Avatar Choice Buttons
        lbl_avatars = QLabel("SELECT COURTROOM AVATAR PERSONA:")
        lbl_avatars.setFont(get_qt_font(9, bold=True))
        lbl_avatars.setStyleSheet(f"color: {COLOR_GOLD.name()};")
        l_layout.addWidget(lbl_avatars)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(6)
        for av in self.avatars:
            btn = QPushButton(av.capitalize())
            btn.setFont(get_qt_font(9, bold=True))
            btn.clicked.connect(lambda checked=False, a=av: self._select_avatar(a))
            self.avatar_buttons.append(btn)
            btn_row.addWidget(btn)
        l_layout.addLayout(btn_row)

        l_layout.addStretch()

        # Creed Box
        creed_frame = QFrame()
        creed_frame.setStyleSheet("""
            QFrame {
                background-color: #17110e;
                border: 1px solid #3d2b1f;
                border-radius: 6px;
            }
        """)
        c_layout = QVBoxLayout(creed_frame)
        c_layout.setContentsMargins(12, 10, 12, 10)
        c_layout.setSpacing(4)
        c_head = QLabel("⚖ HIGH COURT CREED:")
        c_head.setFont(get_qt_font(9, bold=True))
        c_head.setStyleSheet(f"color: {COLOR_GOLD.name()}; background: transparent; border: none; padding: 0px;")
        c_layout.addWidget(c_head)

        creed_text = QLabel('"In this chamber, accusations mean nothing without sound logical deduction. Truth is entailed by evidence and verified facts."')
        creed_text.setFont(get_qt_font(9, italic=True))
        creed_text.setWordWrap(True)
        creed_text.setStyleSheet(f"color: {COLOR_TEXT_PARCHMENT.name()}; line-height: 140%; background: transparent; border: none; padding: 0px;")
        c_layout.addWidget(creed_text)
        l_layout.addWidget(creed_frame)

        body_layout.addWidget(left_frame)

        # ====================================================
        # Right Column: Career Statistics & Honors
        # ====================================================
        right_frame = QFrame()
        right_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLOR_BG_CARD.name()};
                border: 1px solid {COLOR_BORDER.name()};
                border-radius: 8px;
            }}
        """)
        r_layout = QVBoxLayout(right_frame)
        r_layout.setContentsMargins(18, 16, 18, 16)
        r_layout.setSpacing(12)

        r_header = QLabel("CAREER COURTROOM PERFORMANCE & HONORS")
        r_header.setFont(get_qt_font(11, bold=True))
        r_header.setStyleSheet(f"color: {COLOR_GOLD.name()};")
        r_layout.addWidget(r_header)

        # 4 Metric Cards Grid
        grid = QGridLayout()
        grid.setSpacing(12)

        self.lbl_stat_score = self._create_stat_card("TOTAL SCORE", "0 PTS", COLOR_GOLD, grid, 0, 0)
        self.lbl_stat_won = self._create_stat_card("CASES WON", "0 / 0", COLOR_ACCENT_GREEN, grid, 0, 1)
        self.lbl_stat_high = self._create_stat_card("HIGHEST SCORE", "0 PTS", COLOR_ACCENT_BLUE, grid, 1, 0)
        self.lbl_stat_ratio = self._create_stat_card("WIN RATIO", "0%", COLOR_GOLD_LIGHT, grid, 1, 1)
        r_layout.addLayout(grid)

        # Achievements Section
        ach_head = QLabel("HONORS & BARRISTER ACHIEVEMENTS:")
        ach_head.setFont(get_qt_font(11, bold=True))
        ach_head.setStyleSheet(f"color: {COLOR_GOLD.name()}; margin-top: 8px;")
        r_layout.addWidget(ach_head)

        scroll_ach = QScrollArea()
        scroll_ach.setWidgetResizable(True)
        scroll_ach.setStyleSheet("background-color: transparent; border: none;")

        self.ach_container = QWidget()
        self.ach_layout = QVBoxLayout(self.ach_container)
        self.ach_layout.setSpacing(8)
        self.ach_layout.addStretch()

        scroll_ach.setWidget(self.ach_container)
        r_layout.addWidget(scroll_ach, stretch=1)

        body_layout.addWidget(right_frame, stretch=1)
        main_layout.addLayout(body_layout, stretch=1)

        self._refresh_display()

    def _create_stat_card(self, title: str, val: str, color, grid: QGridLayout, r: int, c: int) -> QLabel:
        card = QFrame()
        card.setFixedHeight(82)
        card.setStyleSheet("""
            QFrame {
                background-color: #17110e;
                border: 1px solid #4a3221;
                border-radius: 8px;
            }
        """)
        l = QVBoxLayout(card)
        l.setContentsMargins(14, 8, 14, 8)
        l.setSpacing(3)

        lbl_t = QLabel(title)
        lbl_t.setFont(get_qt_font(9, bold=True))
        lbl_t.setStyleSheet(f"color: {COLOR_TEXT_PARCHMENT.name()}; background: transparent; border: none; padding: 0px;")
        l.addWidget(lbl_t)

        lbl_v = QLabel(val)
        lbl_v.setFont(get_qt_font(16, bold=True))
        lbl_v.setStyleSheet(f"color: {color.name()}; background: transparent; border: none; padding: 0px;")
        lbl_v.setFixedHeight(30)
        l.addWidget(lbl_v)

        grid.addWidget(card, r, c)
        return lbl_v

    def _select_avatar(self, aid: str):
        self.game_state.profile.avatar_id = aid
        self.avatar_preview.set_character(aid, self.game_state.profile.name)
        self.sound_service.play("click")
        self._update_avatar_button_styles()
        self.notify.emit("INFO", f"Avatar persona updated to {aid.capitalize()}!")

    def _update_avatar_button_styles(self):
        curr = self.game_state.profile.avatar_id or "lawyer"
        for i, btn in enumerate(self.avatar_buttons):
            aid = self.avatars[i]
            if aid == curr:
                btn.setStyleSheet("padding: 6px 0; background-color: #6b4420; color: #fff; border: 1px solid #d4af37; border-radius: 4px;")
            else:
                btn.setStyleSheet("padding: 6px 0; background-color: #211713; color: #a08c70; border: 1px solid #3d2b1f; border-radius: 4px;")

    def _save_profile(self):
        new_name = self.txt_name.text().strip()
        if new_name:
            self.game_state.profile.name = new_name
            self.game_state.player_name = new_name
            self.avatar_preview.set_character(self.game_state.profile.avatar_id or "lawyer", new_name)

        self.save_service.save_profile(self.game_state.profile)
        self.sound_service.play("evidence")
        self.notify.emit("SUCCESS", "Barrister Profile Saved Successfully!")

    def _refresh_display(self):
        prof = self.game_state.profile
        self.txt_name.setText(prof.name)
        self.lbl_rank_badge.setText(f"👑 {prof.get_rank()}")
        self.avatar_preview.set_character(prof.avatar_id or "lawyer", prof.name)
        self._update_avatar_button_styles()

        # Stats
        self.lbl_stat_score.setText(f"{prof.total_score} PTS")
        self.lbl_stat_won.setText(f"{prof.cases_won} / {prof.cases_completed}")
        self.lbl_stat_high.setText(f"{prof.highest_score} PTS")
        ratio = int((prof.cases_won / max(1, prof.cases_completed)) * 100)
        self.lbl_stat_ratio.setText(f"{ratio}%")

        # Achievements
        while self.ach_layout.count() > 1:
            child = self.ach_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        achievements_list = [
            ("Bar Examination Gold Medal", "Mastered fundamental propositional deduction principles.", True),
            ("Counsel of the Crown", "Achieved over 500 cumulative points in judicial hearings.", prof.total_score >= 500),
            ("Master of Inference", "Successfully refuted suspect alibis with forensic evidence.", prof.cases_won >= 2),
            ("Lord Chief Justice's Gavel", "Solved all master-level complex homicides.", prof.total_score >= 1200)
        ]

        for name, desc, unlocked in achievements_list:
            card = QFrame()
            bg_col = "#182818" if unlocked else "#17110e"
            bdr_col = COLOR_ACCENT_GREEN.name() if unlocked else "#3d2b1f"
            card.setStyleSheet(f"""
                QFrame {{
                    background-color: {bg_col};
                    border: 1px solid {bdr_col};
                    border-radius: 6px;
                }}
            """)

            l = QHBoxLayout(card)
            l.setContentsMargins(12, 8, 12, 8)
            l.setSpacing(12)

            icon_lbl = QLabel("🏆" if unlocked else "🔒")
            icon_lbl.setFont(get_qt_font(14))
            icon_lbl.setStyleSheet(f"color: {COLOR_GOLD.name() if unlocked else COLOR_TEXT_MUTED.name()}; background: transparent; border: none; padding: 0px;")
            l.addWidget(icon_lbl)

            col = QVBoxLayout()
            col.setSpacing(2)
            n_lbl = QLabel(name)
            n_lbl.setFont(get_qt_font(10, bold=True))
            n_lbl.setStyleSheet(f"color: {COLOR_GOLD.name() if unlocked else COLOR_TEXT_MUTED.name()}; background: transparent; border: none; padding: 0px;")
            col.addWidget(n_lbl)

            d_lbl = QLabel(desc)
            d_lbl.setFont(get_qt_font(9))
            d_lbl.setStyleSheet(f"color: {COLOR_TEXT_PARCHMENT.name() if unlocked else COLOR_TEXT_MUTED.name()}; background: transparent; border: none; padding: 0px;")
            col.addWidget(d_lbl)
            col.addWidget(d_lbl)

            l.addLayout(col, stretch=1)
            self.ach_layout.insertWidget(self.ach_layout.count() - 1, card)

    def on_enter_screen(self):
        self._refresh_display()

