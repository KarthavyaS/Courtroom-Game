"""Main Dashboard Hub for LOGIC COURTROOM.
Serves as the primary operational headquarters for the player:
- Displays player name, title, rank badge, and career statistics.
- Highlights unfinished active investigations with a prominent Continue Card.
- Provides intuitive access to New Cases, Case Files, Case Creator, Leaderboard, Tutorial, and Settings.
"""

import pygame
import math
from typing import Callable, Optional
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, BACKGROUND, DARK_BROWN, WOOD_BROWN,
    LIGHT_PARCHMENT, CARD_BG, GOLD, GOLD_LIGHT, WHITE, MUTED_TEXT,
    ACCENT_RED, ACCENT_GREEN, ACCENT_BLUE, get_font
)
from services.game_state import GameState
from services.save_service import SaveService
from services.sound_service import get_sound_service
from components.animated_button import AnimatedButton
from components.animation import ParticleSystem

class Dashboard:
    """Central player headquarters and navigation dashboard."""

    def __init__(
        self,
        screen: pygame.Surface,
        game_state: GameState,
        save_service: SaveService,
        on_start_case: Callable[[], None],
        on_continue_case: Callable[[], None],
        on_profile: Callable[[], None],
        on_create_case: Callable[[], None],
        on_leaderboard: Callable[[], None],
        on_tutorial: Callable[[], None],
        on_settings: Callable[[], None],
        on_exit: Callable[[], None]
    ):
        self.screen = screen
        self.game_state = game_state
        self.save_service = save_service
        self.on_start_case = on_start_case
        self.on_continue_case = on_continue_case
        self.on_profile = on_profile
        self.on_create_case = on_create_case
        self.on_leaderboard = on_leaderboard
        self.on_tutorial = on_tutorial
        self.on_settings = on_settings
        self.on_exit = on_exit
        self.sound_service = get_sound_service()

        self.anim_tick = 0
        self.particles = ParticleSystem(max_particles=25)
        self.has_active_save = self.save_service.has_active_save()
        self.active_save_summary = self.save_service.get_active_save_summary()

        # Build Action Grid Buttons
        self.buttons = []
        self._build_interface()

    def _build_interface(self) -> None:
        self.buttons.clear()

        # Top Right Profile button
        self.btn_profile = AnimatedButton(
            SCREEN_WIDTH - 210, 15, 180, 42,
            f"👤 {self.game_state.profile.name[:12]}",
            font_size=11, bg_color=(60, 45, 38), on_click=self.on_profile
        )
        self.buttons.append(self.btn_profile)

        # Active case continue button if present
        if self.has_active_save:
            self.btn_continue = AnimatedButton(
                SCREEN_WIDTH - 300, 168, 240, 44,
                "RESUME CASE ➔", font_size=12, bg_color=ACCENT_GREEN,
                on_click=self.on_continue_case
            )
            self.buttons.append(self.btn_continue)

        # Menu Action Grid
        grid_y = 260 if self.has_active_save else 180
        col_w = 310
        row_h = 76
        gap_x = 24
        gap_y = 18

        x1 = 60
        x2 = x1 + col_w + gap_x
        x3 = x2 + col_w + gap_x

        # Row 1
        b_new = AnimatedButton(x1, grid_y, col_w, row_h, "📂 NEW INVESTIGATION\nSelect an open criminal case", font_size=12, bg_color=(145, 80, 30), border_color=(255, 200, 80), on_click=self.on_start_case)
        b_files = AnimatedButton(x2, grid_y, col_w, row_h, "📁 MY CASE FILES\nBrowse solved & custom cases", font_size=12, bg_color=(35, 85, 140), border_color=(120, 190, 255), on_click=self.on_start_case)
        b_create = AnimatedButton(x3, grid_y, col_w, row_h, "✍ CREATE A CASE\nAuthor custom AI legal mysteries", font_size=12, bg_color=(110, 45, 115), border_color=(220, 140, 240), on_click=self.on_create_case)

        # Row 2
        grid_y2 = grid_y + row_h + gap_y
        b_lead = AnimatedButton(x1, grid_y2, col_w, row_h, "🏆 HALL OF JUSTICE\nLeaderboard & high scores", font_size=12, bg_color=(30, 120, 65), border_color=(100, 230, 140), on_click=self.on_leaderboard)
        b_tut = AnimatedButton(x2, grid_y2, col_w, row_h, "🎓 ACADEMY / HOW TO PLAY\nReview 7-step interactive guide", font_size=12, bg_color=(25, 95, 125), border_color=(90, 210, 240), on_click=self.on_tutorial)
        b_sett = AnimatedButton(x3, grid_y2, col_w, row_h, "⚙ SETTINGS & AUDIO\nConfigure sound, text & reset", font_size=12, bg_color=(60, 50, 75), border_color=(180, 160, 220), on_click=self.on_settings)

        self.buttons.extend([b_new, b_files, b_create, b_lead, b_tut, b_sett])

        # Bottom Exit button
        btn_exit_y = SCREEN_HEIGHT - 65
        self.btn_exit = AnimatedButton(60, btn_exit_y, 150, 42, "✖ EXIT COURT", font_size=11, bg_color=(140, 35, 30), border_color=(255, 120, 110), on_click=self.on_exit)
        self.buttons.append(self.btn_exit)

    def handle_events(self, events) -> None:
        for event in events:
            for btn in self.buttons:
                btn.handle_event(event)

    def update(self, dt: float = 0.016) -> None:
        self.anim_tick += 1
        self.particles.update(dt)
        if self.anim_tick % 25 == 0:
            import random
            self.particles.emit(random.randint(50, SCREEN_WIDTH - 50), random.randint(100, SCREEN_HEIGHT - 50), count=2, color=(215, 175, 90), speed_mult=0.6)
        for btn in self.buttons:
            btn.update(dt)

    def draw(self) -> None:
        self.screen.fill(BACKGROUND)
        self.particles.draw(self.screen)

        # Header Bar
        pygame.draw.rect(self.screen, WOOD_BROWN, (0, 0, SCREEN_WIDTH, 70))
        pygame.draw.line(self.screen, GOLD, (0, 70), (SCREEN_WIDTH, 70), 2)

        # Title & Subtitle
        crest_font = get_font(22)
        self.screen.blit(crest_font.render("⚖", True, GOLD), (35, 20))

        title_font = get_font(17, bold=True)
        self.screen.blit(title_font.render("LOGIC COURTROOM — HEADQUARTERS", True, GOLD), (68, 14))

        # Career Stats Pills
        p = self.game_state.profile
        stats_pills = [
            (f"RANK: {p.get_rank().upper()}", GOLD, (60, 45, 25)),
            (f"SCORE: {p.total_score} PTS", (120, 210, 255), (25, 45, 65)),
            (f"WON: {p.verdicts_won}/{p.cases_completed}", ACCENT_GREEN, (25, 55, 35))
        ]
        px = 68
        for label, txt_col, bg_col in stats_pills:
            t_surf = get_font(9, bold=True).render(label, True, txt_col)
            pill_w = t_surf.get_width() + 16
            pill_rect = pygame.Rect(px, 40, pill_w, 20)
            pygame.draw.rect(self.screen, bg_col, pill_rect, border_radius=10)
            pygame.draw.rect(self.screen, txt_col, pill_rect, 1, border_radius=10)
            self.screen.blit(t_surf, (px + 8, 43))
            px += pill_w + 10

        # Active Case Banner if active save exists
        if self.has_active_save and self.active_save_summary:
            sav = self.active_save_summary
            ban_rect = pygame.Rect(60, 95, SCREEN_WIDTH - 120, 140)
            pygame.draw.rect(self.screen, CARD_BG, ban_rect, border_radius=10)
            pygame.draw.rect(self.screen, GOLD_LIGHT, ban_rect, 2, border_radius=10)

            # Left Badge
            pygame.draw.rect(self.screen, (50, 35, 25), (ban_rect.x + 18, ban_rect.y + 18, 100, 104), border_radius=8)
            pygame.draw.rect(self.screen, GOLD, (ban_rect.x + 18, ban_rect.y + 18, 100, 104), 1, border_radius=8)
            self.screen.blit(get_font(28).render("🔍", True, GOLD), (ban_rect.x + 50, ban_rect.y + 35))
            self.screen.blit(get_font(10, bold=True).render(f"{sav['progress_pct']}% DONE", True, ACCENT_GREEN), (ban_rect.x + 36, ban_rect.y + 90))

            # Case Info
            info_x = ban_rect.x + 135
            self.screen.blit(get_font(10, bold=True).render("IN-PROGRESS INVESTIGATION", True, GOLD), (info_x, ban_rect.y + 20))
            self.screen.blit(get_font(16, bold=True).render(sav["case_title"], True, WHITE), (info_x, ban_rect.y + 38))

            stage_name = sav["stage"].replace("_", " ").title()
            det_txt = f"Current Stage: {stage_name} • Evidence Discovered: {sav['collected_count']}/{sav['total_evidence']} • Saved: {sav['timestamp']}"
            self.screen.blit(get_font(11).render(det_txt, True, LIGHT_PARCHMENT), (info_x, ban_rect.y + 68))

            # Small progress bar
            pb_rect = pygame.Rect(info_x, ban_rect.y + 96, 320, 10)
            pygame.draw.rect(self.screen, (30, 20, 15), pb_rect, border_radius=5)
            fill_w = int(pb_rect.width * (sav["progress_pct"] / 100.0))
            if fill_w > 0:
                pygame.draw.rect(self.screen, ACCENT_GREEN, (pb_rect.x, pb_rect.y, fill_w, pb_rect.height), border_radius=5)

        # Draw Buttons
        for btn in self.buttons:
            btn.draw(self.screen)
