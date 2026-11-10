"""Screen Navigation Controller for PySide6 LOGIC COURTROOM.
Manages screen transitions via QStackedWidget, coordinates top navigation bar stages,
handles aliases, relays notifications, and invokes lifecycle hooks.
"""

from typing import Optional, Dict
from PySide6.QtCore import QObject, Slot
from PySide6.QtWidgets import QStackedWidget, QWidget

from services.game_state import GameState
from services.save_service import SaveService
from services.case_service import CaseService
from app_qt.widgets.navigation_bar import NavigationBarQt
from app_qt.widgets.toast_notification import ToastNotification

# Screens
from app_qt.screens.welcome_screen import WelcomeScreenQt
from app_qt.screens.tutorial_screen import TutorialScreenQt
from app_qt.screens.dashboard_screen import DashboardScreenQt
from app_qt.screens.case_selection_screen import CaseSelectionScreenQt
from app_qt.screens.case_briefing_screen import CaseBriefingScreenQt
from app_qt.screens.crime_scene_screen import CrimeSceneScreenQt
from app_qt.screens.suspect_details_screen import SuspectDetailsScreenQt
from app_qt.screens.evidence_view_screen import EvidenceViewScreenQt
from app_qt.screens.case_board_screen import CaseBoardScreenQt
from app_qt.screens.notebook_screen import NotebookScreenQt
from app_qt.screens.argument_builder_screen import ArgumentBuilderScreenQt
from app_qt.screens.courtroom_screen import CourtroomScreenQt
from app_qt.screens.results_screen import ResultsScreenQt
from app_qt.screens.settings_screen import SettingsScreenQt
from app_qt.screens.create_case_screen import CreateCaseScreenQt
from app_qt.screens.leaderboard_screen import LeaderboardScreenQt
from app_qt.screens.profile_screen import ProfileScreenQt


class ScreenNavigator(QObject):
    """Central screen routing and lifecycle orchestrator."""

    ALIASES = {
        "welcome": "welcome",
        "tutorial": "tutorial",
        "dashboard": "dashboard",
        "hub": "dashboard",
        "case_selection": "case_selection",
        "cases": "case_selection",
        "select_case": "case_selection",
        "briefing": "case_briefing",
        "case_briefing": "case_briefing",
        "crime_scene": "crime_scene",
        "scene": "crime_scene",
        "suspects": "suspect_details",
        "suspect_details": "suspect_details",
        "evidence": "evidence_view",
        "evidence_view": "evidence_view",
        "case_board": "case_board",
        "board": "case_board",
        "notebook": "notebook",
        "arguments": "argument_builder",
        "argument_builder": "argument_builder",
        "courtroom": "courtroom",
        "court": "courtroom",
        "trial": "courtroom",
        "enter_court": "courtroom",
        "enter court": "courtroom",
        "enter_courtroom": "courtroom",
        "enter courtroom": "courtroom",
        "enter_trial": "courtroom",
        "enter trial": "courtroom",
        "results": "results",
        "settings": "settings",
        "create_case": "create_case",
        "leaderboard": "leaderboard",
        "profile": "profile",
    }

    INVESTIGATION_STAGES = {
        "case_briefing": "briefing",
        "crime_scene": "crime_scene",
        "suspect_details": "suspects",
        "evidence_view": "evidence",
        "case_board": "case_board",
        "notebook": "notebook",
        "argument_builder": "arguments",
        "courtroom": "courtroom"
    }

    def __init__(
        self,
        stacked_widget: QStackedWidget,
        nav_bar: NavigationBarQt,
        game_state: GameState,
        save_service: SaveService,
        case_service: CaseService,
        toast: ToastNotification,
        parent=None
    ):
        super().__init__(parent)
        self.stacked_widget = stacked_widget
        self.nav_bar = nav_bar
        self.game_state = game_state
        self.save_service = save_service
        self.case_service = case_service
        self.toast = toast

        self.screens: Dict[str, QWidget] = {}
        self.current_screen_id: str = "welcome"

        self._init_screens()
        self._wire_signals()

    def _init_screens(self):
        # 1. Welcome
        self._register("welcome", WelcomeScreenQt(self.game_state, self.save_service))

        # 2. Tutorial
        self._register("tutorial", TutorialScreenQt(self.game_state, self.save_service))

        # 3. Dashboard
        self._register("dashboard", DashboardScreenQt(self.game_state, self.save_service))

        # 4. Case Selection
        self._register("case_selection", CaseSelectionScreenQt(self.game_state, self.case_service, self.save_service))

        # 5. Case Briefing
        self._register("case_briefing", CaseBriefingScreenQt(self.game_state, self.save_service))

        # 6. Crime Scene
        self._register("crime_scene", CrimeSceneScreenQt(self.game_state, self.save_service))

        # 7. Suspect Details
        self._register("suspect_details", SuspectDetailsScreenQt(self.game_state, self.save_service))

        # 8. Evidence View
        self._register("evidence_view", EvidenceViewScreenQt(self.game_state, self.save_service))

        # 9. Case Board
        self._register("case_board", CaseBoardScreenQt(self.game_state, self.save_service))

        # 10. Notebook
        self._register("notebook", NotebookScreenQt(self.game_state, self.save_service))

        # 11. Argument Builder
        self._register("argument_builder", ArgumentBuilderScreenQt(self.game_state, self.save_service))

        # 12. Courtroom
        self._register("courtroom", CourtroomScreenQt(self.game_state, self.save_service))

        # 13. Results
        self._register("results", ResultsScreenQt(self.game_state, self.save_service))

        # 14. Settings
        self._register("settings", SettingsScreenQt(self.game_state, self.save_service))

        # 15. Create Case
        self._register("create_case", CreateCaseScreenQt(self.game_state, self.case_service, self.save_service))

        # 16. Leaderboard
        self._register("leaderboard", LeaderboardScreenQt(self.save_service))

        # 17. Profile
        self._register("profile", ProfileScreenQt(self.game_state, self.save_service))

    def _register(self, screen_id: str, widget: QWidget):
        self.screens[screen_id] = widget
        self.stacked_widget.addWidget(widget)

        # Wire navigate & notify signals
        if hasattr(widget, "navigate"):
            widget.navigate.connect(self.go_to_screen)
        if hasattr(widget, "notify"):
            widget.notify.connect(self._on_notify)

        # Legacy signals fallback wiring
        if hasattr(widget, "start_game"):
            widget.start_game.connect(lambda: self.go_to_screen("dashboard"))
        if hasattr(widget, "continue_game"):
            widget.continue_game.connect(lambda: self.go_to_screen("briefing" if self.game_state.current_case else "dashboard"))
        if hasattr(widget, "enter_crime_scene"):
            widget.enter_crime_scene.connect(lambda: self.go_to_screen("crime_scene"))
        if hasattr(widget, "proceed_to_suspects"):
            widget.proceed_to_suspects.connect(lambda: self.go_to_screen("suspects"))
        if hasattr(widget, "proceed_to_board"):
            widget.proceed_to_board.connect(lambda: self.go_to_screen("case_board"))
        if hasattr(widget, "tutorial_finished"):
            widget.tutorial_finished.connect(lambda: self.go_to_screen("dashboard"))
        if hasattr(widget, "start_case"):
            widget.start_case.connect(lambda: self.go_to_screen("case_selection"))
        if hasattr(widget, "open_profile"):
            widget.open_profile.connect(lambda: self.go_to_screen("profile"))
        if hasattr(widget, "create_case"):
            widget.create_case.connect(lambda: self.go_to_screen("create_case"))
        if hasattr(widget, "open_leaderboard"):
            widget.open_leaderboard.connect(lambda: self.go_to_screen("leaderboard"))
        if hasattr(widget, "open_tutorial"):
            widget.open_tutorial.connect(lambda: self.go_to_screen("tutorial"))
        if hasattr(widget, "open_settings"):
            widget.open_settings.connect(lambda: self.go_to_screen("settings"))

    def _wire_signals(self):
        self.nav_bar.stage_selected.connect(self.go_to_screen)

    @Slot(str, str)
    def _on_notify(self, category: str, message: str):
        self.toast.show_message(message=message, category=category)

    @Slot(str)
    def go_to_screen(self, target_id: str):
        normalized = self.ALIASES.get(target_id.lower(), target_id.lower())
        if normalized not in self.screens:
            normalized = "dashboard"

        # Ensure active case is loaded if entering an investigation stage
        if normalized in self.INVESTIGATION_STAGES and self.game_state.current_case is None:
            cases = self.case_service.get_all_cases()
            if cases:
                self.game_state.set_case(cases[0])
                self.save_service.save_active_game(self.game_state)

        screen = self.screens[normalized]
        self.stacked_widget.setCurrentWidget(screen)
        self.current_screen_id = normalized

        # Lifecycle callback
        if hasattr(screen, "on_enter_screen"):
            screen.on_enter_screen()

        # Update Top Navigation Bar visibility & state
        if normalized in self.INVESTIGATION_STAGES:
            nav_stage = self.INVESTIGATION_STAGES[normalized]
            self.nav_bar.set_active_stage(nav_stage)
            pct = self.game_state.progress.calculate_progress_percentage()
            self.nav_bar.update_progress(pct)
            self.nav_bar.show()
        else:
            self.nav_bar.hide()

