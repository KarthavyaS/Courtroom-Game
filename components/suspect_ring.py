"""Animated Suspect Dock / Suspect Ring component for the Courtroom.
Renders an illuminated circular dock with glowing gold perimeter, pulsating energy rings,
ancient runic glyph markers, and a brass suspect nameplate.
"""

import pygame
import math
from typing import Optional
from config import GOLD, GOLD_LIGHT, WOOD_BROWN, DARK_BROWN, WHITE, ACCENT_RED, MUTED_TEXT, get_font

class SuspectRing:
    """An illuminated courtroom dock where the accused suspect stands."""

    def __init__(self, center_x: int, center_y: int, radius_x: int = 75, radius_y: int = 28):
        self.center_x = center_x
        self.center_y = center_y
        self.radius_x = radius_x
        self.radius_y = radius_y
        self.anim_time = 0.0
        self.pulse_alpha = 180
        self.glow_color = (212, 160, 23)
        self.is_active = True

    def update(self, dt: float = 0.016):
        self.anim_time += dt
        # Smooth sine-based pulsating glow
        self.pulse_alpha = int(140 + 70 * math.sin(self.anim_time * 3.0))

    def draw(self, surface: pygame.Surface, suspect_name: str = "Suspect", suspect_type: str = "accused"):
        self.update()

        cx = self.center_x
        cy = self.center_y
        rx = self.radius_x
        ry = self.radius_y

        # 1. Base Shadow & Wooden Platform Floor
        shadow_rect = pygame.Rect(cx - rx - 8, cy - ry - 4, (rx + 8) * 2, (ry + 8) * 2)
        pygame.draw.ellipse(surface, (15, 10, 8), shadow_rect)

        # Platform Base
        pygame.draw.ellipse(surface, (45, 30, 20), (cx - rx, cy - ry, rx * 2, ry * 2))

        # 2. Outer Pulsating Illuminated Ring (Glow Surface)
        glow_surf = pygame.Surface((rx * 2 + 30, ry * 2 + 20), pygame.SRCALPHA)
        glow_alpha = max(20, min(255, self.pulse_alpha))
        glow_c = (*self.glow_color, int(glow_alpha * 0.4))
        pygame.draw.ellipse(
            glow_surf,
            glow_c,
            (5, 5, rx * 2 + 20, ry * 2 + 10),
            width=5
        )
        surface.blit(glow_surf, (cx - rx - 15, cy - ry - 10))

        # 3. Gold Dock Rim & Inner Filigree
        pygame.draw.ellipse(surface, GOLD_LIGHT, (cx - rx, cy - ry, rx * 2, ry * 2), width=3)
        pygame.draw.ellipse(surface, GOLD, (cx - rx + 6, cy - ry + 3, (rx - 6) * 2, (ry - 3) * 2), width=1)

        # 4. Rotating Runes / Geometric Court Compass Marks
        angle_offset = self.anim_time * 0.8
        for i in range(6):
            theta = angle_offset + i * (math.pi / 3)
            px = int(cx + (rx - 4) * math.cos(theta))
            py = int(cy + (ry - 2) * math.sin(theta))
            pygame.draw.circle(surface, GOLD_LIGHT, (px, py), 2)

        # 5. Brass Suspect Nameplate
        plate_w = 150
        plate_h = 24
        plate_x = cx - plate_w // 2
        plate_y = cy + ry + 4

        # Plate Shadow
        pygame.draw.rect(surface, (10, 5, 2), (plate_x + 2, plate_y + 2, plate_w, plate_h), border_radius=4)
        # Plate Background
        pygame.draw.rect(surface, (35, 24, 16), (plate_x, plate_y, plate_w, plate_h), border_radius=4)
        pygame.draw.rect(surface, GOLD, (plate_x, plate_y, plate_w, plate_h), width=1, border_radius=4)

        # Small red 'ACCUSED' or status badge
        badge_text = suspect_type.upper()
        font_xs = get_font(10, bold=True)
        badge_surf = font_xs.render(f"[{badge_text}]", True, ACCENT_RED)
        surface.blit(badge_surf, (plate_x + 6, plate_y + 4))

        # Suspect Name
        font_sm = get_font(12, bold=True)
        name_surf = font_sm.render(suspect_name[:16], True, WHITE)
        surface.blit(name_surf, (plate_x + 62, plate_y + 4))
