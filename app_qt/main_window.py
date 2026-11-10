"""Main Window Container for PySide6 LOGIC COURTROOM.
Hosts the top navigation bar, central stacked screen widget, and floating toast notification banner.
"""

from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QIcon, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QStackedWidget
)

from services.game_state import GameState
from services.save_service import SaveService
from services.case_service import CaseService
from app_qt.config import SCREEN_WIDTH, SCREEN_HEIGHT
from app_qt.widgets.navigation_bar import NavigationBarQt
from app_qt.widgets.toast_notification import ToastNotification
from app_qt.navigator import ScreenNavigator


class MainWindow(QMainWindow):
    """Primary desktop application window for LOGIC COURTROOM."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("LOGIC COURTROOM — Symbolic AI Legal Deduction")
        self.resize(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.setMinimumSize(960, 600)

        # Core Services
        self.save_service = SaveService()
        self.case_service = CaseService()
        self.game_state = GameState()

        # Load profile and active save if available
        self.game_state.profile = self.save_service.load_profile()
        active_save = self.save_service.load_active_game()
        if active_save and active_save.get("case_id"):
            case = self.case_service.get_case_by_id(active_save["case_id"])
            if case:
                self.game_state.current_case = case
                self.game_state.collected_evidence_ids = set(active_save.get("collected_evidence", []))
                self.game_state.selected_suspect_id = active_save.get("selected_suspect_id")

        # Central Layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        root_layout = QVBoxLayout(central_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # 1. Top Navigation Bar (Shown during investigation stages)
        self.nav_bar = NavigationBarQt(self)
        self.nav_bar.minimize_requested.connect(self.showMinimized)
        root_layout.addWidget(self.nav_bar)

        # 2. Main Stacked Widget
        self.stacked_widget = QStackedWidget(self)
        root_layout.addWidget(self.stacked_widget, stretch=1)

        # 3. Floating Toast Notification
        self.toast = ToastNotification(self)

        # 4. Navigator
        self.navigator = ScreenNavigator(
            stacked_widget=self.stacked_widget,
            nav_bar=self.nav_bar,
            game_state=self.game_state,
            save_service=self.save_service,
            case_service=self.case_service,
            toast=self.toast,
            parent=self
        )

        # Global Shortcuts
        self._setup_shortcuts()

        # Start on Welcome screen (or Dashboard if returning)
        self.navigator.go_to_screen("welcome")

    def _setup_shortcuts(self):
        # Minimize
        min_sc = QShortcut(QKeySequence("Ctrl+M"), self)
        min_sc.activated.connect(self.showMinimized)

        # Audio mute toggle
        mute_sc = QShortcut(QKeySequence("Ctrl+U"), self)
        mute_sc.activated.connect(self.nav_bar._toggle_audio)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Position toast banner at top center
        tw = min(560, self.width() - 80)
        tx = (self.width() - tw) // 2
        ty = 52 if self.nav_bar.isVisible() else 14
        self.toast.setFixedWidth(tw)
        self.toast.move(tx, ty)
        self.toast.raise_()
