"""End-to-End Game Flow and Screen Transition Integration Test.
"""

import unittest
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
from services.case_service import CaseService
from services.save_service import SaveService
from services.game_state import GameState
from services.sound_service import get_sound_service
from screens.welcome import WelcomeScreen
from screens.tutorial import TutorialScreen
from screens.dashboard import Dashboard
from screens.case_selection import CaseSelection
from screens.case_briefing import CaseBriefing
from screens.crime_scene import CrimeScene
from screens.suspect_details import SuspectDetails
from screens.evidence_view import EvidenceView
from screens.case_board import CaseBoard
from screens.investigation_notebook import InvestigationNotebook
from screens.argument_builder import ArgumentBuilder
from screens.courtroom import Courtroom
from screens.results import ResultsScreen
from screens.settings import SettingsScreen

class TestGameFlowIntegration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.font.init()
        cls.screen = pygame.display.set_mode((1100, 680))

    def setUp(self):
        self.case_service = CaseService()
        self.save_service = SaveService()
        self.game_state = GameState()
        self.cases = self.case_service.get_all_cases()
        self.assertTrue(len(self.cases) > 0)
        self.case = self.cases[0]

    def test_screen_lifecycle_and_rendering(self):
        """Validates that all screens instantiate, update, and draw without errors."""
        # 1. Welcome
        welcome = WelcomeScreen(
            screen=self.screen,
            game_state=self.game_state,
            save_service=self.save_service,
            on_start_game=lambda: None,
            on_continue_game=lambda: None
        )
        welcome.update(0.016)
        welcome.draw()

        # 2. Tutorial
        tutorial = TutorialScreen(
            screen=self.screen,
            game_state=self.game_state,
            save_service=self.save_service,
            on_finish=lambda: None
        )
        tutorial.update(0.016)
        tutorial.draw()

        # 3. Dashboard
        dashboard = Dashboard(
            screen=self.screen,
            game_state=self.game_state,
            save_service=self.save_service,
            on_start_case=lambda: None,
            on_continue_case=lambda: None,
            on_profile=lambda: None,
            on_create_case=lambda: None,
            on_leaderboard=lambda: None,
            on_tutorial=lambda: None,
            on_settings=lambda: None,
            on_exit=lambda: None
        )
        dashboard.update(0.016)
        dashboard.draw()

        # 4. Case Selection
        case_sel = CaseSelection(
            screen=self.screen,
            case_service=self.case_service,
            on_back=lambda: None,
            on_investigate=lambda c: None,
            save_service=self.save_service
        )
        case_sel.update(0.016)
        case_sel.draw()

        # Set active case
        self.game_state.set_case(self.case)

        # 5. Briefing
        briefing = CaseBriefing(
            screen=self.screen,
            game_state=self.game_state,
            on_nav_dashboard=lambda: None,
            on_enter_crime_scene=lambda: None,
            on_nav_suspects=lambda: None,
            on_nav_evidence=lambda: None,
            on_nav_board=lambda: None,
            on_nav_notebook=lambda: None,
            on_nav_arguments=lambda: None,
            on_nav_courtroom=lambda: None
        )
        briefing.update(0.016)
        briefing.draw()

        # 6. Crime Scene
        scene = CrimeScene(
            screen=self.screen,
            game_state=self.game_state,
            on_nav_dashboard=lambda: None,
            on_nav_briefing=lambda: None,
            on_nav_suspects=lambda: None,
            on_nav_evidence=lambda: None,
            on_nav_board=lambda: None,
            on_nav_notebook=lambda: None,
            on_nav_arguments=lambda: None,
            on_nav_courtroom=lambda: None
        )
        scene.update(0.016)
        scene.draw()

        # 7. Suspect Details
        suspects_scr = SuspectDetails(
            screen=self.screen,
            game_state=self.game_state,
            on_nav_dashboard=lambda: None,
            on_nav_briefing=lambda: None,
            on_nav_scene=lambda: None,
            on_nav_evidence=lambda: None,
            on_nav_board=lambda: None,
            on_nav_notebook=lambda: None,
            on_nav_arguments=lambda: None,
            on_nav_courtroom=lambda: None
        )
        suspects_scr.update(0.016)
        suspects_scr.draw()

        # 8. Evidence View
        ev_view = EvidenceView(
            screen=self.screen,
            game_state=self.game_state,
            on_nav_dashboard=lambda: None,
            on_nav_briefing=lambda: None,
            on_nav_scene=lambda: None,
            on_nav_suspects=lambda: None,
            on_nav_board=lambda: None,
            on_nav_notebook=lambda: None,
            on_nav_arguments=lambda: None,
            on_nav_courtroom=lambda: None
        )
        ev_view.update(0.016)
        ev_view.draw()

        # 9. Case Board
        board = CaseBoard(
            screen=self.screen,
            game_state=self.game_state,
            on_nav_dashboard=lambda: None,
            on_nav_briefing=lambda: None,
            on_nav_scene=lambda: None,
            on_nav_suspects=lambda: None,
            on_nav_evidence=lambda: None,
            on_nav_notebook=lambda: None,
            on_nav_arguments=lambda: None,
            on_nav_courtroom=lambda: None
        )
        board.update(0.016)
        board.draw()

        # 10. Notebook
        notebook = InvestigationNotebook(
            screen=self.screen,
            game_state=self.game_state,
            on_nav_dashboard=lambda: None,
            on_nav_briefing=lambda: None,
            on_nav_scene=lambda: None,
            on_nav_suspects=lambda: None,
            on_nav_evidence=lambda: None,
            on_nav_board=lambda: None,
            on_nav_arguments=lambda: None,
            on_nav_courtroom=lambda: None
        )
        notebook.update(0.016)
        notebook.draw()

        # 11. Argument Builder
        arg_builder = ArgumentBuilder(
            screen=self.screen,
            game_state=self.game_state,
            on_nav_dashboard=lambda: None,
            on_nav_briefing=lambda: None,
            on_nav_scene=lambda: None,
            on_nav_suspects=lambda: None,
            on_nav_evidence=lambda: None,
            on_nav_board=lambda: None,
            on_nav_notebook=lambda: None,
            on_submit_to_court=lambda arg: None
        )
        arg_builder.update(0.016)
        arg_builder.draw()

        # 12. Courtroom
        courtroom = Courtroom(
            screen=self.screen,
            game_state=self.game_state,
            save_service=self.save_service
        )
        courtroom.update(0.016)
        courtroom.draw()

        # 13. Results Screen
        results = ResultsScreen(
            screen=self.screen,
            game_state=self.game_state,
            verdict_data={"verdict": "SUPPORTED", "total_score": 95, "reasoning": "All rules verified."},
            on_review_hearing=lambda: None,
            on_review_case=lambda: None,
            on_play_another=lambda: None,
            on_dashboard=lambda: None
        )
        results.update(0.016)
        results.draw()

        # 14. Settings Screen
        settings = SettingsScreen(
            screen=self.screen,
            game_state=self.game_state,
            save_service=self.save_service,
            on_back=lambda: None,
            on_replay_tutorial=lambda: None
        )
        settings.update(0.016)
        settings.draw()

if __name__ == "__main__":
    unittest.main()
