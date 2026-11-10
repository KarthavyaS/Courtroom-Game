"""
LOGIC COURTROOM - Desktop Artificial Intelligence Legal Game
Main executable entry point and Screen Navigation Orchestrator.
Coordinates the complete player journey:
Welcome -> Tutorial -> Dashboard -> Case Selection -> Briefing -> Crime Scene ->
Suspects -> Evidence -> Case Board -> Notebook -> Arguments -> Courtroom -> Results.
"""

import sys
import os
# Ensure window is centered on launch
os.environ["SDL_VIDEO_CENTERED"] = "1"

#pyright: ignore
import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, GAME_TITLE
from services.case_service import CaseService
from services.save_service import SaveService
from services.game_state import GameState
from services.sound_service import get_sound_service
from components.notification import Notification
from components.animation import ScreenTransition

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
from screens.create_case import CreateCase
from screens.leaderboard import Leaderboard
from screens.profile import ProfileScreen

def main():
    # Initialize Pygame
    pygame.init()
    pygame.font.init()

    # Flexible Resizable Mode (Centered 1100x680, Desktop application with flexible minimize & maximize)
    window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption(GAME_TITLE)
    canvas = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    screen = canvas  # Screens render to virtual crisp canvas
    clock = pygame.time.Clock()

    # Core Services & State
    case_service = CaseService()
    save_service = SaveService()
    sound_service = get_sound_service()
    user_profile = save_service.load_profile()
    game_state = GameState(profile=user_profile)
    notification_ui = Notification()
    transition_mgr = ScreenTransition(duration=0.24)

    # Apply saved audio preferences
    sound_service.set_sound_enabled(user_profile.sound_enabled)
    sound_service.set_music_enabled(user_profile.music_enabled)
    sound_service.set_volume(user_profile.volume)

    current_screen = None

    def transition_to(screen_builder, style="CURTAIN"):
        if current_screen is None:
            screen_builder()
        else:
            sound_service.play("page_turn")
            transition_mgr.start_transition(on_midpoint=screen_builder, style=style)

    # Screen Transition Handlers
    def show_welcome():
        def _build():
            nonlocal current_screen
            current_screen = WelcomeScreen(
                screen=screen,
                game_state=game_state,
                save_service=save_service,
                on_start_game=handle_welcome_start,
                on_continue_game=resume_saved_investigation
            )
        transition_to(_build)

    def handle_welcome_start():
        if not game_state.profile.tutorial_completed:
            show_tutorial()
        else:
            show_dashboard()

    def show_tutorial():
        def _build():
            nonlocal current_screen
            current_screen = TutorialScreen(
                screen=screen,
                game_state=game_state,
                save_service=save_service,
                on_finish=show_dashboard
            )
        transition_to(_build)

    def show_dashboard():
        def _build():
            nonlocal current_screen
            current_screen = Dashboard(
                screen=screen,
                game_state=game_state,
                save_service=save_service,
                on_start_case=show_case_selection,
                on_continue_case=resume_saved_investigation,
                on_profile=show_profile,
                on_create_case=show_create_case,
                on_leaderboard=show_leaderboard,
                on_tutorial=show_tutorial,
                on_settings=show_settings,
                on_exit=exit_game
            )
        transition_to(_build)

    def show_settings():
        def _build():
            nonlocal current_screen
            current_screen = SettingsScreen(
                screen=screen,
                game_state=game_state,
                save_service=save_service,
                on_back=show_dashboard,
                on_replay_tutorial=show_tutorial
            )
        transition_to(_build)

    def show_profile():
        def _build():
            nonlocal current_screen
            current_screen = ProfileScreen(
                screen=screen,
                game_state=game_state,
                save_service=save_service,
                on_back=show_dashboard
            )
        transition_to(_build)

    def show_case_selection():
        def _build():
            nonlocal current_screen
            current_screen = CaseSelection(
                screen=screen,
                case_service=case_service,
                on_back=show_dashboard,
                on_investigate=start_new_investigation,
                save_service=save_service
            )
        transition_to(_build)

    def start_new_investigation(case):
        game_state.set_case(case)
        save_service.save_active_game(game_state)
        show_case_briefing()

    def resume_saved_investigation():
        active_data = save_service.load_active_game()
        if not active_data or not active_data.get("case_id"):
            show_case_selection()
            return

        case = case_service.get_case_by_id(active_data["case_id"])
        if not case:
            show_case_selection()
            return

        game_state.restore_from_save(case, active_data)
        stage = active_data.get("stage", "briefing")

        if stage == "crime_scene":
            show_crime_scene()
        elif stage == "suspects":
            show_suspect_details()
        elif stage == "evidence":
            show_evidence_view()
        elif stage == "case_board":
            show_case_board()
        elif stage == "notebook":
            show_notebook()
        elif stage == "arguments":
            show_argument_builder()
        elif stage == "courtroom":
            show_courtroom()
        else:
            show_case_briefing()

    def show_case_briefing():
        def _build():
            nonlocal current_screen
            current_screen = CaseBriefing(
                screen=screen,
                game_state=game_state,
                on_nav_dashboard=show_dashboard,
                on_enter_crime_scene=show_crime_scene,
                on_nav_suspects=show_suspect_details,
                on_nav_evidence=show_evidence_view,
                on_nav_board=show_case_board,
                on_nav_notebook=show_notebook,
                on_nav_arguments=show_argument_builder,
                on_nav_courtroom=show_courtroom,
                save_service=save_service
            )
        transition_to(_build)

    def show_crime_scene():
        def _build():
            nonlocal current_screen
            current_screen = CrimeScene(
                screen=screen,
                game_state=game_state,
                on_nav_dashboard=show_dashboard,
                on_nav_briefing=show_case_briefing,
                on_nav_suspects=show_suspect_details,
                on_nav_evidence=show_evidence_view,
                on_nav_board=show_case_board,
                on_nav_notebook=show_notebook,
                on_nav_arguments=show_argument_builder,
                on_nav_courtroom=show_courtroom,
                save_service=save_service
            )
        transition_to(_build)

    def show_suspect_details():
        def _build():
            nonlocal current_screen
            current_screen = SuspectDetails(
                screen=screen,
                game_state=game_state,
                on_nav_dashboard=show_dashboard,
                on_nav_briefing=show_case_briefing,
                on_nav_scene=show_crime_scene,
                on_nav_evidence=show_evidence_view,
                on_nav_board=show_case_board,
                on_nav_notebook=show_notebook,
                on_nav_arguments=show_argument_builder,
                on_nav_courtroom=show_courtroom,
                save_service=save_service
            )
        transition_to(_build)

    def show_evidence_view():
        def _build():
            nonlocal current_screen
            current_screen = EvidenceView(
                screen=screen,
                game_state=game_state,
                on_nav_dashboard=show_dashboard,
                on_nav_briefing=show_case_briefing,
                on_nav_scene=show_crime_scene,
                on_nav_suspects=show_suspect_details,
                on_nav_board=show_case_board,
                on_nav_notebook=show_notebook,
                on_nav_arguments=show_argument_builder,
                on_nav_courtroom=show_courtroom,
                save_service=save_service
            )
        transition_to(_build)

    def show_case_board():
        def _build():
            nonlocal current_screen
            current_screen = CaseBoard(
                screen=screen,
                game_state=game_state,
                on_nav_dashboard=show_dashboard,
                on_nav_briefing=show_case_briefing,
                on_nav_scene=show_crime_scene,
                on_nav_suspects=show_suspect_details,
                on_nav_evidence=show_evidence_view,
                on_nav_notebook=show_notebook,
                on_nav_arguments=show_argument_builder,
                on_nav_courtroom=show_courtroom,
                save_service=save_service
            )
        transition_to(_build)

    def show_notebook():
        def _build():
            nonlocal current_screen
            current_screen = InvestigationNotebook(
                screen=screen,
                game_state=game_state,
                on_nav_dashboard=show_dashboard,
                on_nav_briefing=show_case_briefing,
                on_nav_scene=show_crime_scene,
                on_nav_suspects=show_suspect_details,
                on_nav_evidence=show_evidence_view,
                on_nav_board=show_case_board,
                on_nav_arguments=show_argument_builder,
                on_nav_courtroom=show_courtroom,
                save_service=save_service
            )
        transition_to(_build)

    def show_argument_builder():
        def _build():
            nonlocal current_screen
            current_screen = ArgumentBuilder(
                screen=screen,
                game_state=game_state,
                on_nav_dashboard=show_dashboard,
                on_nav_briefing=show_case_briefing,
                on_nav_scene=show_crime_scene,
                on_nav_suspects=show_suspect_details,
                on_nav_evidence=show_evidence_view,
                on_nav_board=show_case_board,
                on_nav_notebook=show_notebook,
                on_submit_to_court=show_courtroom,
                on_nav_courtroom=show_courtroom,
                save_service=save_service
            )
        transition_to(_build)

    def show_courtroom(argument=None):
        def _build():
            nonlocal current_screen
            courtroom_screen = Courtroom(
                screen=screen,
                game_state=game_state,
                save_service=save_service,
                on_navigate_case_file=show_case_briefing,
                on_navigate_crime_scene=show_crime_scene,
                on_navigate_suspects=show_suspect_details,
                on_navigate_evidence=show_evidence_view,
                on_navigate_arguments=show_argument_builder,
                on_case_selection=show_case_selection,
                on_view_leaderboard=show_leaderboard,
                on_view_results=show_results
            )
            if argument:
                courtroom_screen._process_argument(argument.custom_text or ", ".join(argument.premises))
            current_screen = courtroom_screen
        transition_to(_build)

    def show_results(verdict_data):
        def _build():
            nonlocal current_screen
            current_screen = ResultsScreen(
                screen=screen,
                game_state=game_state,
                verdict_data=verdict_data,
                on_review_hearing=lambda: show_courtroom(),
                on_review_case=show_case_briefing,
                on_play_another=show_case_selection,
                on_dashboard=show_dashboard,
                save_service=save_service
            )
        transition_to(_build)

    def show_create_case():
        def _build():
            nonlocal current_screen
            current_screen = CreateCase(
                screen=screen,
                case_service=case_service,
                game_state=game_state,
                on_back=show_dashboard,
                on_case_created=on_case_created
            )
        transition_to(_build)

    def on_case_created(new_case):
        show_case_selection()

    def show_leaderboard():
        def _build():
            nonlocal current_screen
            current_screen = Leaderboard(
                screen=screen,
                save_service=save_service,
                on_back=show_dashboard
            )
        transition_to(_build)

    def exit_game():
        pygame.quit()
        sys.exit(0)

    # Launch initial screen
    show_welcome()

    def minimize_window_app():
        """Minimizes the desktop window via SDL and Windows API."""
        try:
            pygame.display.iconify()
        except Exception:
            pass
        try:
            import ctypes
            hwnd = pygame.display.get_wm_info().get("window")
            if hwnd:
                ctypes.windll.user32.ShowWindow(hwnd, 6) # SW_MINIMIZE = 6
        except Exception:
            pass

    # Main Game Loop
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        events = pygame.event.get()
        win_w, win_h = window.get_size()

        # Handle system window events
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                window = pygame.display.set_mode(event.size, pygame.RESIZABLE)
            elif event.type == pygame.KEYDOWN:
                # Ctrl+M or F11 or Esc to flexibly minimize window
                if (event.key == pygame.K_m and (event.mod & pygame.KMOD_CTRL)) or event.key == pygame.K_F11:
                    minimize_window_app()

        # Translate mouse coordinates if window is scaled
        if win_w != SCREEN_WIDTH or win_h != SCREEN_HEIGHT:
            scale = min(win_w / SCREEN_WIDTH, win_h / SCREEN_HEIGHT)
            offset_x = (win_w - SCREEN_WIDTH * scale) / 2
            offset_y = (win_h - SCREEN_HEIGHT * scale) / 2
            for event in events:
                if hasattr(event, "pos"):
                    mx = int((event.pos[0] - offset_x) / scale)
                    my = int((event.pos[1] - offset_y) / scale)
                    event.pos = (max(0, min(SCREEN_WIDTH, mx)), max(0, min(SCREEN_HEIGHT, my)))

        transition_mgr.update(dt)

        if current_screen:
            if transition_mgr.state == "NONE":
                current_screen.handle_events(events)
            try:
                current_screen.update(dt)
            except TypeError:
                current_screen.update()

        game_state.update()

        # Check for toast alerts
        if game_state.notification_message:
            notification_ui.show(game_state.notification_message, category=game_state.notification_category)
            game_state.notification_message = None

        notification_ui.update()

        if current_screen:
            current_screen.draw()

        # Render live transition overlay
        transition_mgr.draw(screen)

        notification_ui.draw(screen)

        # Blit canvas to window surface
        if win_w == SCREEN_WIDTH and win_h == SCREEN_HEIGHT:
            window.blit(canvas, (0, 0))
        else:
            scale = min(win_w / SCREEN_WIDTH, win_h / SCREEN_HEIGHT)
            scaled_w = max(1, int(SCREEN_WIDTH * scale))
            scaled_h = max(1, int(SCREEN_HEIGHT * scale))
            offset_x = int((win_w - scaled_w) / 2)
            offset_y = int((win_h - scaled_h) / 2)
            scaled_canvas = pygame.transform.smoothscale(canvas, (scaled_w, scaled_h))
            window.fill((14, 10, 8))
            window.blit(scaled_canvas, (offset_x, offset_y))

        pygame.display.flip()

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()