"""Unified Top Navigation Bar for LOGIC COURTROOM.
Provides seamless stage-to-stage navigation across the complete investigation journey.
"""

import pygame
from typing import Callable, Optional, Dict, Any, List
from config import (
    SCREEN_WIDTH, WOOD_BROWN, CARD_BG, GOLD, GOLD_LIGHT, WHITE,
    MUTED_TEXT, ACCENT_RED, ACCENT_GREEN, ACCENT_BLUE, DARK_BROWN, get_font
)
from components.animated_button import AnimatedButton
from services.game_state import GameState

class NavigationBar:
    """Standardized top navigation bar for all investigation screens."""

    def __init__(
        self,
        current_stage: str,
        game_state: GameState,
        on_nav_dashboard: Callable[[], None],
        on_nav_briefing: Optional[Callable[[], None]] = None,
        on_nav_scene: Optional[Callable[[], None]] = None,
        on_nav_suspects: Optional[Callable[[], None]] = None,
        on_nav_evidence: Optional[Callable[[], None]] = None,
        on_nav_board: Optional[Callable[[], None]] = None,
        on_nav_notebook: Optional[Callable[[], None]] = None,
        on_nav_arguments: Optional[Callable[[], None]] = None,
        on_nav_courtroom: Optional[Callable[[], None]] = None
    ):
        self.current_stage = current_stage
        self.game_state = game_state
        self.on_nav_dashboard = on_nav_dashboard
        self.on_nav_briefing = on_nav_briefing
        self.on_nav_scene = on_nav_scene
        self.on_nav_suspects = on_nav_suspects
        self.on_nav_evidence = on_nav_evidence
        self.on_nav_board = on_nav_board
        self.on_nav_notebook = on_nav_notebook
        self.on_nav_arguments = on_nav_arguments
        self.on_nav_courtroom = on_nav_courtroom

        self.buttons: List[AnimatedButton] = []
        self._build_buttons()

    def _build_buttons(self) -> None:
        self.buttons.clear()
        y = 10
        h = 32

        # 1. Back to Dashboard
        btn_dash = AnimatedButton(15, y, 75, h, "⌂ HUB", font_size=11, bg_color=(60, 45, 38), on_click=self.on_nav_dashboard)
        self.buttons.append(btn_dash)

        # Tabs
        tabs_config = [
            ("briefing", "BRIEFING", 85, self.on_nav_briefing, None),
            ("crime_scene", "SCENE", 75, self.on_nav_scene, None),
            ("suspects", "SUSPECTS", 95, self.on_nav_suspects, None),
            ("evidence", "EVIDENCE", 100, self.on_nav_evidence, None),
            ("case_board", "BOARD", 80, self.on_nav_board, (60, 80, 110)),
            ("notebook", "NOTEBOOK", 95, self.on_nav_notebook, (70, 90, 60)),
            ("arguments", "ARGUMENTS", 105, self.on_nav_arguments, (130, 60, 40)),
            ("courtroom", "⚖ COURT", 95, self.on_nav_courtroom, (115, 45, 35))
        ]

        curr_x = 98
        for stage_id, label, width, callback, custom_bg in tabs_config:
            is_active = (self.current_stage == stage_id)
            if is_active:
                btn = AnimatedButton(
                    curr_x, y, width, h, label,
                    font_size=11,
                    bg_color=(150, 95, 35),
                    border_color=(255, 220, 90),
                    text_color=WHITE
                )
                btn.is_selected = True
            else:
                btn = AnimatedButton(
                    curr_x, y, width, h, label,
                    font_size=11,
                    bg_color=custom_bg or (45, 35, 30),
                    border_color=(140, 110, 75),
                    text_color=(240, 230, 215),
                    on_click=callback
                )
        # Window Minimize Button (Ctrl+M shortcut supported)
        btn_min = AnimatedButton(
            SCREEN_WIDTH - 42, y, 32, h, "—",
            font_size=13, bg_color=(50, 32, 26), border_color=GOLD,
            tooltip="Minimize Window (Ctrl+M)", on_click=self._minimize_window
        )
        self.buttons.append(btn_min)

    def _minimize_window(self) -> None:
        """Minimizes the desktop game window via SDL and Win32."""
        try:
            pygame.display.iconify()
        except Exception:
            pass
        try:
            import ctypes
            hwnd = pygame.display.get_wm_info().get("window")
            if hwnd:
                ctypes.windll.user32.ShowWindow(hwnd, 6)
        except Exception:
            pass

    def handle_events(self, events) -> None:
        for event in events:
            for btn in self.buttons:
                btn.handle_event(event)

    def update(self, dt: float = 0.016) -> None:
        for btn in self.buttons:
            btn.update(dt)

        # Update dynamic badges
        if self.game_state.current_case:
            col_count = len(self.game_state.collected_evidence_ids)
            tot_count = len(self.game_state.current_case.evidence_list)
            for btn in self.buttons:
                if "EVIDENCE" in btn.text:
                    if self.current_stage == "evidence":
                        btn.text = f"EVIDENCE ({col_count}/{tot_count})"
                    else:
                        btn.text = f"EVID ({col_count}/{tot_count})"
                elif "SUSPECTS" in btn.text:
                    sus_count = len(self.game_state.current_case.suspects)
                    done_sus = len(self.game_state.progress.interviewed_suspect_ids)
                    btn.text = f"SUSPECTS ({done_sus}/{sus_count})"

    def draw(self, surface: pygame.Surface) -> None:
        # Header background bar
        pygame.draw.rect(surface, WOOD_BROWN, (0, 0, SCREEN_WIDTH, 52))
        pygame.draw.line(surface, GOLD, (0, 52), (SCREEN_WIDTH, 52), 2)

        for btn in self.buttons:
            btn.draw(surface)

        # Active case indicator badge on far right
        if self.game_state.current_case:
            pct = self.game_state.progress.calculate_progress_percentage()
            badge_rect = pygame.Rect(SCREEN_WIDTH - 245, 12, 195, 28)
            pygame.draw.rect(surface, CARD_BG, badge_rect, border_radius=5)
            pygame.draw.rect(surface, GOLD_LIGHT, badge_rect, 1, border_radius=5)

            font = get_font(11, bold=True)
            txt = font.render(f"Progress: {pct}%", True, GOLD)
            surface.blit(txt, (badge_rect.x + 8, badge_rect.y + 6))

            # Small progress bar inside badge
            bar_rect = pygame.Rect(badge_rect.x + 95, badge_rect.y + 8, 90, 12)
            pygame.draw.rect(surface, (40, 30, 25), bar_rect, border_radius=3)
            fill_w = int(bar_rect.width * (pct / 100.0))
            if fill_w > 0:
                pygame.draw.rect(surface, ACCENT_GREEN, (bar_rect.x, bar_rect.y, fill_w, bar_rect.height), border_radius=3)
