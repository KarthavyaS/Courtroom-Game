"""Progress Tracker Component for LOGIC COURTROOM.
Renders an elegant HUD / drawer displaying the 7-stage case investigation checklist,
action completion status, and contextual tips.
"""

import pygame
from typing import Dict, Any, List
from config import (
    CARD_BG, DARK_BROWN, GOLD, GOLD_LIGHT, WHITE, MUTED_TEXT,
    ACCENT_GREEN, ACCENT_RED, ACCENT_BLUE, get_font
)
from services.game_state import GameState

class ProgressTracker:
    """Renders the case checklist and investigation milestones."""

    def __init__(self, x: int, y: int, width: int, height: int):
        self.rect = pygame.Rect(x, y, width, height)

    def draw(self, surface: pygame.Surface, game_state: GameState) -> None:
        # Background card
        pygame.draw.rect(surface, CARD_BG, self.rect, border_radius=8)
        pygame.draw.rect(surface, GOLD_LIGHT, self.rect, 1, border_radius=8)

        # Header
        header_font = get_font(13, bold=True)
        title_surf = header_font.render("INVESTIGATION CHECKLIST", True, GOLD)
        surface.blit(title_surf, (self.rect.x + 14, self.rect.y + 12))

        # Overall completion percentage
        pct = game_state.progress.calculate_progress_percentage()
        pct_font = get_font(12, bold=True)
        pct_surf = pct_font.render(f"{pct}% COMPLETE", True, ACCENT_GREEN if pct >= 80 else GOLD_LIGHT)
        surface.blit(pct_surf, (self.rect.right - pct_surf.get_width() - 14, self.rect.y + 12))

        # Progress bar
        bar_bg = pygame.Rect(self.rect.x + 14, self.rect.y + 34, self.rect.width - 28, 8)
        pygame.draw.rect(surface, (30, 20, 15), bar_bg, border_radius=4)
        fill_w = int(bar_bg.width * (pct / 100.0))
        if fill_w > 0:
            pygame.draw.rect(surface, ACCENT_GREEN, (bar_bg.x, bar_bg.y, fill_w, 8), border_radius=4)

        # Checklist Items
        items = game_state.progress.get_checklist_items()
        item_y = self.rect.y + 50
        item_font = get_font(11)
        check_font = get_font(11, bold=True)

        for item in items:
            is_done = item["done"]
            box_rect = pygame.Rect(self.rect.x + 14, item_y + 2, 14, 14)
            if is_done:
                pygame.draw.rect(surface, ACCENT_GREEN, box_rect, border_radius=3)
                chk = check_font.render("✓", True, WHITE)
                surface.blit(chk, (box_rect.x + 2, box_rect.y - 1))
            else:
                pygame.draw.rect(surface, (45, 35, 30), box_rect, border_radius=3)
                pygame.draw.rect(surface, MUTED_TEXT, box_rect, 1, border_radius=3)

            # Text label
            label_col = WHITE if is_done else (180, 170, 160)
            lbl_surf = item_font.render(item["label"], True, label_col)
            surface.blit(lbl_surf, (self.rect.x + 36, item_y))

            item_y += 24
