"""Main Menu Screen for LOGIC COURTROOM.
Features animated ambient lighting, Scales of Justice physics, and quick profile stats.
"""
#pyright: ignore
import pygame
import math
from typing import Callable, Optional
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, BACKGROUND, DARK_BROWN, WOOD_BROWN,
    LIGHT_PARCHMENT, GOLD, GOLD_LIGHT, WHITE, MUTED_TEXT, get_font
)
from services.game_state import GameState
from components.button import Button
from components.illustrations import draw_animated_scales, AmbientParticleSystem

class MainMenu:
    """Vintage courtroom-themed main menu with rich animations and profile integration."""

    def __init__(
        self,
        screen: pygame.Surface,
        game_state: GameState,
        on_start: Callable[[], None],
        on_profile: Callable[[], None],
        on_create: Callable[[], None],
        on_leaderboard: Callable[[], None],
        on_exit: Callable[[], None]
    ):
        self.screen = screen
        self.game_state = game_state
        self.on_start = on_start
        self.on_profile = on_profile
        self.on_create = on_create
        self.on_leaderboard = on_leaderboard
        self.on_exit = on_exit

        btn_w = 360
        btn_h = 52
        center_x = (SCREEN_WIDTH - btn_w) // 2
        start_y = 315
        spacing = 64

        self.btn_start = Button(
            center_x, start_y, btn_w, btn_h,
            "START INVESTIGATION", font_size=19, bg_color=WOOD_BROWN, hover_color=GOLD, on_click=self.on_start
        )
        self.btn_profile = Button(
            center_x, start_y + spacing, btn_w, btn_h,
            "ADVOCATE PROFILE & HONORS", font_size=17, bg_color=WOOD_BROWN, on_click=self.on_profile
        )
        self.btn_create = Button(
            center_x, start_y + (spacing * 2), btn_w, btn_h,
            "CREATE A CUSTOM CASE", font_size=17, bg_color=WOOD_BROWN, on_click=self.on_create
        )
        self.btn_leaderboard = Button(
            center_x, start_y + (spacing * 3), btn_w, btn_h,
            "COURT OF RECORD / LEADERBOARD", font_size=17, bg_color=WOOD_BROWN, on_click=self.on_leaderboard
        )
        self.btn_exit = Button(
            center_x, start_y + (spacing * 4), btn_w, btn_h,
            "EXIT GAME", font_size=16, bg_color=(90, 45, 35), on_click=self.on_exit
        )

        self.buttons = [self.btn_start, self.btn_profile, self.btn_create, self.btn_leaderboard, self.btn_exit]
        self.particles = AmbientParticleSystem(count=35)
        self.anim_tick = 0

    def handle_events(self, events):
        for event in events:
            for btn in self.buttons:
                btn.handle_event(event)

    def update(self):
        self.anim_tick += 1
        self.particles.update()

    def draw(self):
        self.screen.fill(BACKGROUND)
        self.particles.draw(self.screen)

        # Draw decorative vintage courtroom outer frame
        pygame.draw.rect(self.screen, DARK_BROWN, (16, 16, SCREEN_WIDTH - 32, SCREEN_HEIGHT - 32), 4, border_radius=16)
        pygame.draw.rect(self.screen, GOLD, (24, 24, SCREEN_WIDTH - 48, SCREEN_HEIGHT - 48), 2, border_radius=12)

        # Draw background pillars
        for x_pillar in [55, 1155]:
            pygame.draw.rect(self.screen, (225, 210, 180), (x_pillar, 40, 70, SCREEN_HEIGHT - 80), border_radius=6)
            pygame.draw.rect(self.screen, (190, 175, 145), (x_pillar, 40, 70, SCREEN_HEIGHT - 80), 2, border_radius=6)
            for f in range(3):
                pygame.draw.line(self.screen, (205, 190, 160), (x_pillar + 18 + f * 17, 70), (x_pillar + 18 + f * 17, SCREEN_HEIGHT - 100), 2)

        # Header Title Banner
        header_rect = pygame.Rect(180, 45, SCREEN_WIDTH - 360, 240)
        # Banner shadow
        pygame.draw.rect(self.screen, (40, 20, 10, 80), (header_rect.x + 4, header_rect.y + 6, header_rect.width, header_rect.height), border_radius=16)
        # Banner base
        pygame.draw.rect(self.screen, WOOD_BROWN, header_rect, border_radius=16)
        # Gold inner border
        pygame.draw.rect(self.screen, GOLD, (header_rect.x + 8, header_rect.y + 8, header_rect.width - 16, header_rect.height - 16), 3, border_radius=12)

        # Animated Scales of Justice emblem
        draw_animated_scales(self.screen, (SCREEN_WIDTH // 2, header_rect.y + 50), self.anim_tick)

        # Title
        font_title = get_font("Georgia", 48, bold=True)
        title_surf = font_title.render("LOGIC COURTROOM", True, LIGHT_PARCHMENT)
        self.screen.blit(title_surf, title_surf.get_rect(center=(SCREEN_WIDTH // 2, header_rect.y + 125)))

        # Gold divider line
        pygame.draw.line(self.screen, GOLD, (header_rect.x + 80, header_rect.y + 162), (header_rect.right - 80, header_rect.y + 162), 2)

        # Tagline
        font_tag = get_font("Georgia", 17, italic=True)
        tag_surf = font_tag.render("Where Logic Decides the Verdict", True, GOLD_LIGHT)
        self.screen.blit(tag_surf, tag_surf.get_rect(center=(SCREEN_WIDTH // 2, header_rect.y + 185)))

        # Advocate Profile Quick Status
        prof = self.game_state.profile
        prof_txt = f"Lead Counsel: {prof.name}   |   Rank: {prof.get_rank()}   |   Score: {prof.total_score} pts"
        prof_surf = get_font("Georgia", 13).render(prof_txt, True, (230, 215, 185))
        self.screen.blit(prof_surf, prof_surf.get_rect(center=(SCREEN_WIDTH // 2, header_rect.y + 215)))

        # Draw Buttons
        for btn in self.buttons:
            btn.draw(self.screen)

        # Footer label
        font_foot = get_font("Georgia", 13)
        foot_surf = font_foot.render("Traditional AI Propositional Resolution • Deterministic Judicial Proofs", True, MUTED_TEXT)
        self.screen.blit(foot_surf, foot_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 35)))