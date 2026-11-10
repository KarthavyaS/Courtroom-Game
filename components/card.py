"""Vintage Parchment Card Component for LOGIC COURTROOM.
"""

import pygame
from typing import Optional, Tuple, List
from config import (
    CARD_BG, LIGHT_PARCHMENT, GOLD, WOOD_BROWN, DARK_BROWN,
    MUTED_TEXT, get_font
)

class Card:
    """A reusable vintage parchment card with borders and interactive styling."""

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        title: str = "",
        subtitle: str = "",
        border_radius: int = 12
    ):
        self.rect = pygame.Rect(x, y, width, height)
        self.title = title
        self.subtitle = subtitle
        self.border_radius = border_radius
        self.is_hovered = False
        self.is_selected = False

    def is_clicked(self, pos: Tuple[int, int]) -> bool:
        return self.rect.collidepoint(pos)

    def draw(
        self,
        surface: pygame.Surface,
        bg_color: Optional[Tuple[int, int, int]] = None,
        border_color: Optional[Tuple[int, int, int]] = None
    ) -> None:
        mouse_pos = pygame.mouse.get_pos()
        self.is_hovered = self.rect.collidepoint(mouse_pos)

        # Background color
        card_bg = bg_color or (LIGHT_PARCHMENT if self.is_hovered or self.is_selected else CARD_BG)
        border_col = border_color or (GOLD if self.is_selected or self.is_hovered else WOOD_BROWN)

        # Draw card shadow
        shadow_rect = self.rect.copy()
        shadow_rect.y += 4
        shadow_rect.x += 2
        pygame.draw.rect(surface, (50, 30, 15, 60), shadow_rect, border_radius=self.border_radius)

        # Card base
        pygame.draw.rect(surface, card_bg, self.rect, border_radius=self.border_radius)

        # Card outer border
        pygame.draw.rect(surface, border_col, self.rect, width=2, border_radius=self.border_radius)

        # Inner subtle gold fillet
        inner_rect = self.rect.inflate(-8, -8)
        if inner_rect.width > 0 and inner_rect.height > 0:
            pygame.draw.rect(surface, (190, 145, 75, 120), inner_rect, width=1, border_radius=max(1, self.border_radius - 4))

        # Header title
        if self.title:
            font_title = get_font("Georgia", 19, bold=True)
            title_surf = font_title.render(self.title, True, DARK_BROWN)
            surface.blit(title_surf, (self.rect.x + 16, self.rect.y + 14))

        if self.subtitle:
            font_sub = get_font("Georgia", 14, italic=True)
            sub_surf = font_sub.render(self.subtitle, True, MUTED_TEXT)
            surface.blit(sub_surf, (self.rect.x + 16, self.rect.y + 38))
