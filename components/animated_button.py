"""Animated Vintage Button with hover scale, glow, press feedback, and tooltips for LOGIC COURTROOM.
Features multi-line text support with automatic line spacing and high-contrast vibrant typography.
"""

import pygame
import math
from typing import Optional, Tuple, Callable, List
from config import (
    WOOD_BROWN, GOLD, GOLD_LIGHT, LIGHT_PARCHMENT, WHITE, DARK_BROWN,
    get_font
)
from services.sound_service import get_sound_service
from components.animation import ease_out_quad

class AnimatedButton:
    """A polished, smoothly animating button with scale, sound, multiline layout, and vibrant contrast."""

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        text: str,
        font_size: int = 14,
        bg_color: Tuple[int, int, int] = WOOD_BROWN,
        hover_color: Optional[Tuple[int, int, int]] = None,
        text_color: Tuple[int, int, int] = WHITE,
        border_color: Tuple[int, int, int] = GOLD,
        border_radius: int = 7,
        on_click: Optional[Callable[[], None]] = None,
        tooltip: Optional[str] = None,
        is_disabled: bool = False
    ):
        self.orig_rect = pygame.Rect(x, y, width, height)
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font_size = max(12, font_size)
        self.font = get_font(self.font_size, bold=True)
        self.sub_font = get_font(max(12, self.font_size - 2), bold=False)
        self.bg_color = bg_color
        self.hover_color = hover_color or self._calc_hover_color(bg_color)
        self.text_color = text_color
        self.border_color = border_color
        self.border_radius = border_radius
        self.on_click = on_click
        self.tooltip = tooltip
        self.is_disabled = is_disabled
        self.is_selected = False
        self.is_pressed = False
        self.hover_anim = 0.0  # 0.0 to 1.0
        self.sound_service = get_sound_service()

    def _calc_hover_color(self, base_color: Tuple[int, int, int]) -> Tuple[int, int, int]:
        """Calculates a brighter, more vibrant version of the base background color for hovering."""
        r = min(255, int(base_color[0] * 1.35) + 20)
        g = min(255, int(base_color[1] * 1.35) + 20)
        b = min(255, int(base_color[2] * 1.35) + 20)
        return (r, g, b)

    def handle_event(self, event: pygame.event.Event) -> bool:
        if self.is_disabled:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.orig_rect.collidepoint(event.pos):
                self.is_pressed = True
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.is_pressed:
                self.is_pressed = False
                if self.orig_rect.collidepoint(event.pos):
                    self.sound_service.play("click")
                    if self.on_click:
                        self.on_click()
                    return True
        return False

    def update(self, dt: float = 0.016):
        mouse_pos = pygame.mouse.get_pos()
        hovered = self.orig_rect.collidepoint(mouse_pos) and not self.is_disabled

        target = 1.0 if hovered else 0.0
        speed = 12.0 if hovered else 8.0
        self.hover_anim += (target - self.hover_anim) * min(1.0, speed * dt)

    def draw(self, surface: pygame.Surface):
        self.update()

        # Calculate animated bounds
        scale = 1.0 + (0.03 * ease_out_quad(self.hover_anim))
        if self.is_pressed:
            scale = 0.97

        new_w = int(self.orig_rect.width * scale)
        new_h = int(self.orig_rect.height * scale)
        cx, cy = self.orig_rect.center
        draw_rect = pygame.Rect(cx - new_w // 2, cy - new_h // 2 + (2 if self.is_pressed else 0), new_w, new_h)

        # Drop shadow for 3D depth
        if not self.is_disabled and not self.is_pressed:
            shadow = draw_rect.copy()
            shadow.y += 2
            pygame.draw.rect(surface, (15, 10, 8, 90), shadow, border_radius=self.border_radius)

        # Color evaluation with high contrast
        if self.is_disabled:
            bg = (55, 45, 40)
            border = (90, 75, 65)
            txt_col = (190, 180, 170)
        elif self.is_selected:
            bg = (150, 95, 45)
            border = (255, 220, 100)
            txt_col = WHITE
        elif self.hover_anim > 0.05:
            t = self.hover_anim
            bg = (
                int(self.bg_color[0] * (1 - t) + self.hover_color[0] * t),
                int(self.bg_color[1] * (1 - t) + self.hover_color[1] * t),
                int(self.bg_color[2] * (1 - t) + self.hover_color[2] * t)
            )
            border = (255, 225, 110)
            txt_col = WHITE
        else:
            bg = self.bg_color
            border = self.border_color
            txt_col = self.text_color

        # Shape rendering: Chamfered geometric polygon with corner accents
        from components.ui_shapes import draw_chamfered_rect
        cut_size = min(8, draw_rect.height // 4)
        draw_chamfered_rect(
            surface=surface,
            rect=draw_rect,
            bg_color=bg,
            border_color=border,
            cut=cut_size,
            border_width=2,
            corner_brackets=(self.hover_anim > 0.4 or self.is_selected),
            inner_glow=(self.hover_anim > 0.1)
        )

        # Render Text with Proper Dynamic Fitting & Zero Overlap
        lines = [line.strip() for line in self.text.split("\n") if line.strip()]
        avail_w = draw_rect.width - 14
        avail_h = draw_rect.height - 4

        if len(lines) == 1:
            line_str = lines[0]
            f = self.font
            # Downscale font if string exceeds width
            if f.size(line_str)[0] > avail_w:
                f = self.sub_font
            if f.size(line_str)[0] > avail_w:
                f = get_font(max(12, self.font_size - 3), bold=True)

            shadow_surf = f.render(line_str, True, (10, 8, 6))
            surface.blit(shadow_surf, shadow_surf.get_rect(center=(draw_rect.centerx + 1, draw_rect.centery + 1)))
            text_surf = f.render(line_str, True, txt_col)
            surface.blit(text_surf, text_surf.get_rect(center=draw_rect.center))
        elif len(lines) >= 2:
            # Multiline button (Header + Subtitles)
            rendered_surfs = []
            total_text_h = 0
            
            for i, line_str in enumerate(lines):
                if i == 0:
                    f = self.font
                    col = txt_col
                    if f.size(line_str)[0] > avail_w:
                        f = self.sub_font
                else:
                    f = self.sub_font
                    col = (245, 230, 200) if not self.is_disabled else (170, 160, 150)
                    if f.size(line_str)[0] > avail_w:
                        f = get_font(12, bold=False)
                
                s_surf = f.render(line_str, True, col)
                s_shadow = f.render(line_str, True, (10, 8, 6))
                rendered_surfs.append((s_surf, s_shadow))
                total_text_h += s_surf.get_height()

            gap = max(2, (avail_h - total_text_h) // (len(lines) + 1))
            cur_y = draw_rect.centery - (total_text_h + (len(lines) - 1) * gap) // 2

            for s_surf, s_shadow in rendered_surfs:
                sx = draw_rect.centerx - s_surf.get_width() // 2
                surface.blit(s_shadow, (sx + 1, cur_y + 1))
                surface.blit(s_surf, (sx, cur_y))
                cur_y += s_surf.get_height() + gap

        # Tooltip on hover
        if self.tooltip and self.hover_anim > 0.6:
            tip_font = get_font(13, bold=True)
            tip_surf = tip_font.render(self.tooltip, True, WHITE)
            tip_w = min(surface.get_width() - 40, tip_surf.get_width() + 24)
            tip_box = pygame.Rect(draw_rect.centerx - tip_w // 2, max(50, draw_rect.top - 34), tip_w, 28)
            draw_chamfered_rect(surface, tip_box, (20, 14, 10), GOLD, cut=5, border_width=1)
            surface.blit(tip_surf, tip_surf.get_rect(center=tip_box.center))


