"""Panel Component for LOGIC COURTROOM.
Draws vintage textured panels, dialogues, and scrollable content containers.
"""

import pygame
from typing import Optional, Tuple, List
from config import (
    WOOD_BROWN, DARK_BROWN, LIGHT_PARCHMENT, GOLD, GOLD_LIGHT,
    WHITE, get_font
)

class Panel:
    """A vintage wooden/parchment panel for content grouping."""

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        title: str = "",
        bg_color: Tuple[int, int, int] = LIGHT_PARCHMENT,
        border_color: Tuple[int, int, int] = GOLD,
        border_radius: int = 12
    ):
        self.rect = pygame.Rect(x, y, width, height)
        self.title = title
        self.bg_color = bg_color
        self.border_color = border_color
        self.border_radius = border_radius
        self.scroll_y = 0

    def draw(self, surface: pygame.Surface) -> None:
        # Shadow
        shadow_rect = self.rect.copy()
        shadow_rect.y += 4
        pygame.draw.rect(surface, (40, 20, 10, 80), shadow_rect, border_radius=self.border_radius)

        # Panel surface
        pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=self.border_radius)

        # Dual borders
        pygame.draw.rect(surface, self.border_color, self.rect, width=3, border_radius=self.border_radius)

        # Inner decorative border
        inner_rect = self.rect.inflate(-8, -8)
        if inner_rect.width > 0 and inner_rect.height > 0:
            pygame.draw.rect(surface, WOOD_BROWN, inner_rect, width=1, border_radius=max(1, self.border_radius - 4))

        # Title bar if present
        if self.title:
            header_rect = pygame.Rect(self.rect.x + 4, self.rect.y + 4, self.rect.width - 8, 38)
            pygame.draw.rect(surface, WOOD_BROWN, header_rect, border_top_left_radius=self.border_radius - 2, border_top_right_radius=self.border_radius - 2)
            pygame.draw.rect(surface, GOLD, header_rect, width=1, border_top_left_radius=self.border_radius - 2, border_top_right_radius=self.border_radius - 2)

            font = get_font("Georgia", 17, bold=True)
            text_surf = font.render(self.title, True, LIGHT_PARCHMENT)
            surface.blit(text_surf, (header_rect.x + 14, header_rect.y + 8))
