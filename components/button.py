"""Interactive Vintage Button Component for LOGIC COURTROOM.
"""

import pygame
from typing import Optional, Tuple, Callable
from config import (
    WOOD_BROWN, GOLD, GOLD_LIGHT, LIGHT_PARCHMENT, WHITE, DARK_BROWN,
    get_font
)

class Button:
    """A polished vintage-themed interactive button with high contrast and multiline support."""

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        text: str,
        font_size: int = 14,
        bg_color: Tuple[int, int, int] = WOOD_BROWN,
        hover_color: Tuple[int, int, int] = GOLD,
        text_color: Tuple[int, int, int] = WHITE,
        border_color: Tuple[int, int, int] = GOLD,
        border_radius: int = 7,
        on_click: Optional[Callable[[], None]] = None,
        icon_name: Optional[str] = None
    ):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font_size = font_size
        self.font = get_font(font_size, bold=True)
        self.sub_font = get_font(max(9, font_size - 2), bold=False)
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.border_color = border_color
        self.border_radius = border_radius
        self.on_click = on_click
        self.icon_name = icon_name
        self.is_disabled = False
        self.is_selected = False

    def is_clicked(self, pos: Tuple[int, int]) -> bool:
        if self.is_disabled:
            return False
        return self.rect.collidepoint(pos)

    def handle_event(self, event: pygame.event.Event) -> bool:
        if self.is_disabled:
            return False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.on_click:
                    self.on_click()
                return True
        return False

    def draw(self, surface: pygame.Surface) -> None:
        mouse_pos = pygame.mouse.get_pos()
        hovered = self.rect.collidepoint(mouse_pos) and not self.is_disabled

        # Determine background color
        if self.is_disabled:
            bg = (55, 45, 40)
            border = (90, 75, 65)
            txt_col = (190, 180, 170)
        elif self.is_selected:
            bg = (150, 95, 45)
            border = (255, 220, 100)
            txt_col = WHITE
        elif hovered:
            bg = (
                min(255, int(self.bg_color[0] * 1.3) + 20),
                min(255, int(self.bg_color[1] * 1.3) + 20),
                min(255, int(self.bg_color[2] * 1.3) + 20)
            )
            border = (255, 225, 110)
            txt_col = WHITE
        else:
            bg = self.bg_color
            border = self.border_color
            txt_col = self.text_color

        # Drop shadow
        if not self.is_disabled and not self.is_selected:
            shadow_rect = self.rect.copy()
            shadow_rect.y += 2
            pygame.draw.rect(surface, (15, 10, 8, 90), shadow_rect, border_radius=self.border_radius)

        pygame.draw.rect(surface, bg, self.rect, border_radius=self.border_radius)
        pygame.draw.rect(surface, border, self.rect, width=2, border_radius=self.border_radius)

        # Inner highlight
        if not self.is_disabled and self.rect.height > 20:
            inner_rect = self.rect.inflate(-4, -4)
            if inner_rect.width > 0 and inner_rect.height > 0:
                pygame.draw.rect(surface, (255, 255, 255, 35), inner_rect, width=1, border_radius=max(1, self.border_radius - 2))

        # Render button text with multiline support
        lines = self.text.split("\n")
        if len(lines) == 1:
            line_str = lines[0]
            f = self.font
            if f.size(line_str)[0] > (self.rect.width - 12):
                f = self.sub_font

            # Shadow & Text
            sh = f.render(line_str, True, (10, 8, 6))
            surface.blit(sh, sh.get_rect(center=(self.rect.centerx + 1, self.rect.centery + 1)))
            ts = f.render(line_str, True, txt_col)
            surface.blit(ts, ts.get_rect(center=self.rect.center))
        else:
            t_surf = self.font.render(lines[0], True, txt_col)
            s_surf = self.sub_font.render(lines[1], True, (235, 220, 200) if not self.is_disabled else (160, 150, 140))

            total_h = t_surf.get_height() + s_surf.get_height() + 4
            start_y = self.rect.centery - total_h // 2

            t_shadow = self.font.render(lines[0], True, (10, 8, 6))
            surface.blit(t_shadow, (self.rect.centerx - t_surf.get_width() // 2 + 1, start_y + 1))
            surface.blit(t_surf, (self.rect.centerx - t_surf.get_width() // 2, start_y))

            s_y = start_y + t_surf.get_height() + 4
            s_shadow = self.sub_font.render(lines[1], True, (10, 8, 6))
            surface.blit(s_shadow, (self.rect.centerx - s_surf.get_width() // 2 + 1, s_y + 1))
            surface.blit(s_surf, (self.rect.centerx - s_surf.get_width() // 2, s_y))
