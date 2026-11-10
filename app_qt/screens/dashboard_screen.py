"""Investigation Hub and Dashboard Headquarters for PySide6 LOGIC COURTROOM.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton, QFrame, QScrollArea
)
from services.game_state import GameState
from services.save_service import SaveService
from app_qt.config import (
    HEX_GOLD, HEX_GOLD_LIGHT, HEX_ACCENT_GREEN, HEX_LIGHT_PARCHMENT,
    HEX_MUTED_TEXT, HEX_ACCENT_BLUE, HEX_WOOD_BROWN, get_qt_font
)
from app_qt.services.sound_service_qt import get_sound_service_qt


class DashboardScreenQt(QWidget):
    """Central player headquarters and navigation dashboard."""

    navigate = Signal(str)
    notify = Signal(str, str)
    start_case = Signal()
    continue_case = Signal()
    open_profile = Signal()
    create_case = Signal()
    open_leaderboard = Signal()
    open_tutorial = Signal()
    open_settings = Signal()
    exit_game = Signal()

    def __init__(self, game_state: GameState, save_service: SaveService, parent=None):
        super().__init__(parent)
        self.game_state = game_state
        self.save_service = save_service
        self.sound_service = get_sound_service_qt()

        self._build_ui()

    def _build_ui(self):
        # Outer container layout for centering and responsive framing
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(16, 12, 16, 12)
        outer_layout.setSpacing(0)

        # Centered command console frame (prevents over-stretching on wide monitors)
        self.content_widget = QWidget()
        self.content_widget.setMaximumWidth(880)

        main_layout = QVBoxLayout(self.content_widget)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(14)

        # 1. Top Header Bar (Back to Main Menu, Advocate rank, & profile shortcut)
        top_bar = QHBoxLayout()
        top_bar.setSpacing(12)

        btn_menu_top = QPushButton("← MAIN MENU")
        btn_menu_top.setFont(get_qt_font(10, bold=True))
        btn_menu_top.setStyleSheet(f"""
            QPushButton {{
                background-color: #2b1f14;
                color: #c9a050;
                border: 1px solid #5a381e;
                border-radius: 5px;
                padding: 6px 14px;
                min-height: 28px;
            }}
            QPushButton:hover {{
                background-color: #422f1f;
                border: 1px solid {HEX_GOLD};
                color: #ffffff;
            }}
        """)
        btn_menu_top.clicked.connect(self._on_back_to_menu)
        top_bar.addWidget(btn_menu_top)

        header_text_box = QVBoxLayout()
        header_text_box.setSpacing(2)

        self.lbl_welcome = QLabel("INVESTIGATION HEADQUARTERS")
        self.lbl_welcome.setFont(get_qt_font(15, bold=True))
        self.lbl_welcome.setStyleSheet(f"color: {HEX_GOLD}; letter-spacing: 0.5px;")
        header_text_box.addWidget(self.lbl_welcome)

        self.lbl_rank = QLabel("Advocate: Arthur Pendelton  |  Rank: Junior Barrister")
        self.lbl_rank.setStyleSheet(f"font-size: 12px; color: {HEX_GOLD_LIGHT};")
        header_text_box.addWidget(self.lbl_rank)
        top_bar.addLayout(header_text_box, stretch=1)

        btn_prof = QPushButton("👤 ADVOCATE DOSSIER")
        btn_prof.setFont(get_qt_font(10, bold=True))
        btn_prof.setStyleSheet(f"""
            QPushButton {{
                background-color: #3d261b;
                color: #ffd741;
                border: 1px solid #ffd741;
                border-radius: 5px;
                padding: 6px 14px;
                min-height: 28px;
            }}
            QPushButton:hover {{
                background-color: #5c3829;
                color: #ffffff;
            }}
        """)
        btn_prof.clicked.connect(self._on_profile)
        top_bar.addWidget(btn_prof)

        main_layout.addLayout(top_bar)

        # 2. Continue Active Case Card (Shown conditionally)
        self.continue_card = QFrame()
        self.continue_card.setStyleSheet(f"""
            QFrame {{
                background-color: #25160e;
                border: 2px solid #ffd741;
                border-radius: 8px;
            }}
        """)
        c_layout = QHBoxLayout(self.continue_card)
        c_layout.setContentsMargins(16, 10, 16, 10)

        c_info = QVBoxLayout()
        c_info.setSpacing(3)
        self.lbl_active_title = QLabel("ACTIVE CASE IN PROGRESS: THE MIDNIGHT MURDER")
        self.lbl_active_title.setFont(get_qt_font(12, bold=True))
        self.lbl_active_title.setStyleSheet(f"color: {HEX_GOLD}; background: transparent; border: none; padding: 0px;")
        c_info.addWidget(self.lbl_active_title)

        self.lbl_active_meta = QLabel("Current Stage: Crime Scene  |  Evidence Collected: 3/8  |  Progress: 35%")
        self.lbl_active_meta.setFont(get_qt_font(10))
        self.lbl_active_meta.setStyleSheet(f"color: {HEX_LIGHT_PARCHMENT}; background: transparent; border: none; padding: 0px;")
        c_info.addWidget(self.lbl_active_meta)
        c_layout.addLayout(c_info, 1)

        btn_resume = QPushButton("RESUME INVESTIGATION ➔")
        btn_resume.setProperty("class", "btn-success")
        btn_resume.setFont(get_qt_font(10, bold=True))
        btn_resume.setFixedHeight(36)
        btn_resume.clicked.connect(self._on_continue)
        c_layout.addWidget(btn_resume)

        main_layout.addWidget(self.continue_card)

        # 3. 6-Card Action Grid
        grid = QGridLayout()
        grid.setSpacing(14)

        actions = [
            ("📂 NEW INVESTIGATION", "Select an open case from the court docket", "#8f4b1e", "#ffd741", self._on_start),
            ("⚖️ ENTER COURTROOM", "Directly enter the courtroom trial chamber to face the AI Judge", "#7b241c", "#ff6b6b", self._on_courtroom),
            ("✍ CREATE A CASE", "Author custom cases with clues & deduction rules", "#6a2970", "#ce93d8", self._on_create),
            ("🏆 HALL OF JUSTICE", "Review high scores, verdicts & honor records", "#1f6e39", "#81c784", self._on_leaderboard),
            ("🎓 ACADEMY / TUTORIAL", "Review 7-step guide to logic, evidence & court", "#1a5b78", "#4fc3f7", self._on_tutorial),
            ("⚙ SETTINGS & AUDIO", "Configure sound effects, music volume & resets", "#3d324c", "#b39ddb", self._on_settings),
        ]

        for i, (title, subtitle, bg_col, bdr_col, handler) in enumerate(actions):
            row = i // 3
            col = i % 3

            card_btn = QPushButton()
            card_btn.setMinimumHeight(92)
            card_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {bg_col};
                    border: 1px solid {bdr_col};
                    border-radius: 8px;
                    text-align: left;
                    padding: 8px;
                }}
                QPushButton:hover {{
                    border: 2px solid #ffffff;
                }}
            """)
            card_btn.clicked.connect(handler)

            # Custom card text layout inside button
            b_layout = QVBoxLayout(card_btn)
            b_layout.setContentsMargins(12, 8, 12, 8)
            b_layout.setSpacing(4)

            lbl_t = QLabel(title)
            lbl_t.setFont(get_qt_font(11, bold=True))
            lbl_t.setStyleSheet("color: #ffffff; border: none; background: transparent; padding: 0px;")
            lbl_t.setAttribute(Qt.WA_TransparentForMouseEvents)
            b_layout.addWidget(lbl_t)

            lbl_s = QLabel(subtitle)
            lbl_s.setFont(get_qt_font(9))
            lbl_s.setStyleSheet(f"color: {HEX_LIGHT_PARCHMENT}; border: none; background: transparent; padding: 0px;")
            lbl_s.setWordWrap(True)
            lbl_s.setAttribute(Qt.WA_TransparentForMouseEvents)
            b_layout.addWidget(lbl_s)

            grid.addWidget(card_btn, row, col)

        main_layout.addLayout(grid)

        # 4. Bottom Navigation & Exit Bar
        bottom_bar = QHBoxLayout()

        btn_back_bottom = QPushButton("← RETURN TO MAIN MENU")
        btn_back_bottom.setFont(get_qt_font(10, bold=True))
        btn_back_bottom.setStyleSheet(f"""
            QPushButton {{
                background-color: #2b1f14;
                color: #c9a050;
                border: 1px solid #5a381e;
                border-radius: 5px;
                padding: 6px 16px;
                min-height: 28px;
            }}
            QPushButton:hover {{
                background-color: #422f1f;
                border: 1px solid {HEX_GOLD};
                color: #ffffff;
            }}
        """)
        btn_back_bottom.clicked.connect(self._on_back_to_menu)
        bottom_bar.addWidget(btn_back_bottom)

        bottom_bar.addStretch(1)

        btn_exit = QPushButton("✖ EXIT GAME")
        btn_exit.setProperty("class", "btn-danger")
        btn_exit.setFont(get_qt_font(10, bold=True))
        btn_exit.setFixedHeight(34)
        btn_exit.clicked.connect(self._on_exit)
        bottom_bar.addWidget(btn_exit)

        main_layout.addLayout(bottom_bar)

        outer_layout.addWidget(self.content_widget, 0, Qt.AlignHCenter | Qt.AlignVCenter)

    def on_enter_screen(self):
        profile = self.game_state.profile
        self.lbl_welcome.setText(f"INVESTIGATION HEADQUARTERS — {profile.name.upper()}")
        self.lbl_rank.setText(f"Advocate: {profile.name}  |  Rank: {profile.get_rank()}  |  Wins: {profile.verdicts_won}/{profile.cases_completed}")

        has_save = self.save_service.has_active_save()
        self.continue_card.setVisible(has_save)
        if has_save:
            summary = self.save_service.get_active_save_summary()
            if summary:
                self.lbl_active_title.setText(f"ACTIVE INVESTIGATION: {summary.get('case_title', 'Unknown Case').upper()}")
                stage = summary.get("stage", "briefing").replace("_", " ").title()
                col = summary.get("collected_count", 0)
                tot = summary.get("total_evidence", 0)
                pct = summary.get("progress_pct", 0)
                self.lbl_active_meta.setText(f"Stage: {stage}  |  Clues Collected: {col}/{tot}  |  Completion: {pct}%")

    def _on_start(self):
        self.sound_service.play("click")
        self.start_case.emit()
        self.navigate.emit("case_selection")

    def _on_continue(self):
        self.sound_service.play("gavel")
        self.continue_case.emit()
        if self.game_state.current_case:
            self.navigate.emit("briefing")
        else:
            self.navigate.emit("case_selection")

    def _on_courtroom(self):
        self.sound_service.play("gavel")
        self.navigate.emit("courtroom")

    def _on_profile(self):
        self.sound_service.play("click")
        self.open_profile.emit()
        self.navigate.emit("profile")

    def _on_create(self):
        self.sound_service.play("click")
        self.create_case.emit()
        self.navigate.emit("create_case")

    def _on_leaderboard(self):
        self.sound_service.play("click")
        self.open_leaderboard.emit()
        self.navigate.emit("leaderboard")

    def _on_tutorial(self):
        self.sound_service.play("click")
        self.open_tutorial.emit()
        self.navigate.emit("tutorial")

    def _on_settings(self):
        self.sound_service.play("click")
        self.open_settings.emit()
        self.navigate.emit("settings")

    def _on_back_to_menu(self):
        self.sound_service.play("click")
        self.navigate.emit("welcome")

    def _on_exit(self):
        self.sound_service.play("click")
        self.exit_game.emit()
        from PySide6.QtWidgets import QApplication
        app = QApplication.instance()
        if app:
            app.quit()

