"""Leaderboard & Records Screen for LOGIC COURTROOM.
Displays persistent barrister rankings, verdict honors, and deductive test scores
with high-contrast vibrant styling for 1100x680 resolution.
"""

import pygame
from typing import Callable, List, Dict, Any
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, BACKGROUND, DARK_BROWN, WOOD_BROWN,
    LIGHT_PARCHMENT, CARD_BG, GOLD, GOLD_LIGHT, WHITE, MUTED_TEXT,
    ACCENT_RED, ACCENT_GREEN, ACCENT_BLUE, ACCENT_ORANGE, get_font
)
from services.save_service import SaveService
from services.sound_service import get_sound_service
from components.animated_button import AnimatedButton

class Leaderboard:
    """Courtroom Barrister Roll of Honor leaderboard screen."""

    def __init__(
        self,
        screen: pygame.Surface,
        save_service: SaveService,
        on_back: Callable[[], None]
    ):
        self.screen = screen
        self.save_service = save_service
        self.on_back = on_back
        self.sound_service = get_sound_service()

        self.btn_back = AnimatedButton(30, 16, 110, 36, "← HUB", font_size=11, bg_color=(55, 42, 35), on_click=self.on_back)
        self.btn_refresh = AnimatedButton(SCREEN_WIDTH - 150, 16, 120, 36, "REFRESH ↺", font_size=11, bg_color=(40, 85, 140), on_click=self.refresh_records)
        self.records: List[Dict[str, Any]] = []
        self.refresh_records()

    def refresh_records(self):
        self.records = self.save_service.get_leaderboard()

    def handle_events(self, events):
        for event in events:
            self.btn_back.handle_event(event)
            self.btn_refresh.handle_event(event)

    def update(self, dt: float = 0.016):
        self.btn_back.update(dt)
        self.btn_refresh.update(dt)

    def draw(self):
        self.screen.fill(BACKGROUND)

        # Header Bar
        pygame.draw.rect(self.screen, WOOD_BROWN, (0, 0, SCREEN_WIDTH, 56))
        pygame.draw.line(self.screen, GOLD, (0, 56), (SCREEN_WIDTH, 56), 2)

        # Header Title
        t_surf = get_font(18, bold=True).render("HALL OF FAME • COURT OF RECORD", True, GOLD)
        self.screen.blit(t_surf, t_surf.get_rect(center=(SCREEN_WIDTH // 2, 28)))

        self.btn_back.draw(self.screen)
        self.btn_refresh.draw(self.screen)

        # Table Container Panel (x: 35, y: 75, w: 1030, h: 575)
        table_rect = pygame.Rect(35, 75, 1030, 575)
        pygame.draw.rect(self.screen, CARD_BG, table_rect, border_radius=10)
        pygame.draw.rect(self.screen, GOLD_LIGHT, table_rect, width=1, border_radius=10)

        # Table Header Row
        header_rect = pygame.Rect(table_rect.x + 2, table_rect.y + 2, table_rect.width - 4, 38)
        pygame.draw.rect(self.screen, (45, 32, 25), header_rect, border_top_left_radius=8, border_top_right_radius=8)

        th_font = get_font(11, bold=True)
        cols = [
            ("RANK", table_rect.x + 20),
            ("ADVOCATE", table_rect.x + 100),
            ("CASE TITLE", table_rect.x + 320),
            ("VERDICT", table_rect.x + 580),
            ("SCORE", table_rect.x + 750),
            ("DATE FILED", table_rect.x + 880)
        ]

        for col_name, x_pos in cols:
            surf = th_font.render(col_name, True, GOLD)
            self.screen.blit(surf, (x_pos, header_rect.y + 11))

        # Table Data Rows
        if not self.records:
            e_surf = get_font(14, italic=True).render("No courtroom records filed yet. Complete an investigation to earn your place!", True, LIGHT_PARCHMENT)
            self.screen.blit(e_surf, e_surf.get_rect(center=table_rect.center))
            return

        row_y = table_rect.y + 48
        for i, rec in enumerate(self.records[:10]):
            row_rect = pygame.Rect(table_rect.x + 6, row_y - 2, table_rect.width - 12, 44)

            bg_row = (42, 32, 26) if i % 2 == 0 else (30, 22, 18)
            pygame.draw.rect(self.screen, bg_row, row_rect, border_radius=5)
            pygame.draw.rect(self.screen, (75, 58, 45), row_rect, width=1, border_radius=5)

            # Rank badge
            rank_col = GOLD if i == 0 else ((200, 210, 220) if i == 1 else ((220, 150, 90) if i == 2 else LIGHT_PARCHMENT))
            self.screen.blit(get_font(12, bold=True).render(f"#{i+1}", True, rank_col), (cols[0][1], row_y + 11))

            # Advocate
            self.screen.blit(get_font(12, bold=True).render(str(rec.get("player_name", "Anonymous"))[:18], True, WHITE), (cols[1][1], row_y + 11))

            # Case Title
            self.screen.blit(get_font(11).render(str(rec.get("case_title", "Unknown Case"))[:24], True, LIGHT_PARCHMENT), (cols[2][1], row_y + 11))

            # Verdict
            verdict = rec.get("verdict", "INCONCLUSIVE")
            v_col = ACCENT_GREEN if verdict == "SUPPORTED" else ACCENT_ORANGE
            self.screen.blit(get_font(11, bold=True).render(verdict, True, v_col), (cols[3][1], row_y + 11))

            # Score
            score_txt = f"{rec.get('score', 0)} PTS"
            self.screen.blit(get_font(12, bold=True).render(score_txt, True, GOLD_LIGHT), (cols[4][1], row_y + 11))

            # Date
            d_str = str(rec.get("date", rec.get("timestamp", "")))[:16]
            self.screen.blit(get_font(10).render(d_str, True, MUTED_TEXT), (cols[5][1], row_y + 12))

            row_y += 48
