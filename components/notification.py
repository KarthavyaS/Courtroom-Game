"""Notification Banner / Toast Component for LOGIC COURTROOM.
"""

import pygame
from typing import Optional, Tuple
from config import (
    SCREEN_WIDTH, ACCENT_GREEN, ACCENT_RED, GOLD, WOOD_BROWN,
    WHITE, LIGHT_PARCHMENT, get_font
)

class Notification:
    """Displays polished toast notifications across screens."""

    def __init__(self):
        self.message: Optional[str] = None
        self.category: str = "INFO"  # 'SUCCESS', 'WARNING', 'ERROR', 'INFO'
        self.frames_left: int = 0
        self.total_frames: int = 180

    def show(self, message: str, category: str = "INFO", duration_frames: int = 180) -> None:
        self.message = message
        self.category = category.upper()
        self.frames_left = duration_frames
        self.total_frames = duration_frames

    def update(self) -> None:
        if self.frames_left > 0:
            self.frames_left -= 1
            if self.frames_left <= 0:
                self.message = None

    def draw(self, surface: pygame.Surface) -> None:
        if not self.message or self.frames_left <= 0:
            return

        font = get_font("Georgia", 16, bold=True)
        text_surf = font.render(self.message, True, WHITE)

        padding_x = 24
        padding_y = 12
        width = text_surf.get_width() + (padding_x * 2) + 30
        height = text_surf.get_height() + (padding_y * 2)

        x = (SCREEN_WIDTH - width) // 2
        y = 20

        # Colors by category
        if self.category == "SUCCESS":
            bg_col = ACCENT_GREEN
            border_col = (120, 220, 140)
            prefix = "✓ "
        elif self.category == "ERROR":
            bg_col = ACCENT_RED
            border_col = (250, 140, 130)
            prefix = "✗ "
        elif self.category == "WARNING":
            bg_col = (190, 120, 30)
            border_col = GOLD
            prefix = "⚠ "
        else:
            bg_col = WOOD_BROWN
            border_col = GOLD
            prefix = "ℹ "

        rect = pygame.Rect(x, y, width, height)

        # Draw shadow
        shadow = rect.copy()
        shadow.y += 3
        pygame.draw.rect(surface, (0, 0, 0, 90), shadow, border_radius=10)

        # Draw banner
        pygame.draw.rect(surface, bg_col, rect, border_radius=10)
        pygame.draw.rect(surface, border_col, rect, width=2, border_radius=10)

        # Draw icon and text
        full_text = prefix + self.message
        full_surf = font.render(full_text, True, WHITE)
        surface.blit(full_surf, full_surf.get_rect(center=rect.center))
