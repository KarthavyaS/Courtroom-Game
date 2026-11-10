"""Innovative Geometric & Ornate UI Shape Drawing Utilities for LOGIC COURTROOM.
Provides chamfered (cut-corner) panels, hexagonal badges, ribbon banners,
ornamental corner brackets, metallic rivets, and dynamic glowing glassmorphism.
"""

import pygame
import math
from typing import Tuple, List, Optional
from config import GOLD, GOLD_LIGHT, GOLD_DARK, WHITE, DARK_BROWN, WOOD_BROWN, get_font

def get_chamfered_points(rect: pygame.Rect, cut: int = 10) -> List[Tuple[int, int]]:
    """Calculates the 8 vertices of a rectangle with 45-degree cut (chamfered) corners."""
    c = min(cut, rect.width // 4, rect.height // 4)
    x1, y1 = rect.left, rect.top
    x2, y2 = rect.right, rect.bottom
    return [
        (x1 + c, y1),
        (x2 - c, y1),
        (x2, y1 + c),
        (x2, y2 - c),
        (x2 - c, y2),
        (x1 + c, y2),
        (x1, y2 - c),
        (x1, y1 + c),
    ]

def draw_chamfered_rect(
    surface: pygame.Surface,
    rect: pygame.Rect,
    bg_color: Tuple[int, int, int],
    border_color: Optional[Tuple[int, int, int]] = None,
    cut: int = 10,
    border_width: int = 2,
    corner_brackets: bool = True,
    inner_glow: bool = False
):
    """Draws a stylized high-tech/courtroom chamfered polygon with beveled corners,
    inner glow, and ornate corner brackets.
    """
    points = get_chamfered_points(rect, cut)
    if len(points) < 8:
        pygame.draw.rect(surface, bg_color, rect, border_radius=6)
        return

    # Drop shadow
    shadow_rect = rect.copy()
    shadow_rect.y += 3
    shadow_pts = get_chamfered_points(shadow_rect, cut)
    shadow_surf = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    pygame.draw.polygon(shadow_surf, (10, 8, 6, 120), shadow_pts)
    surface.blit(shadow_surf, (0, 0))

    # Main Body Polygon
    pygame.draw.polygon(surface, bg_color, points)

    # Inner Glow Line
    if inner_glow and rect.width > 24 and rect.height > 24:
        inner_rect = rect.inflate(-6, -6)
        inner_pts = get_chamfered_points(inner_rect, max(4, cut - 3))
        glow_surf = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        pygame.draw.polygon(glow_surf, (255, 255, 255, 28), inner_pts, width=1)
        surface.blit(glow_surf, (0, 0))

    # Border Polygon
    if border_color:
        pygame.draw.polygon(surface, border_color, points, width=border_width)

    # Decorative Corner Brackets / Rivets
    if corner_brackets and cut >= 6:
        b_col = border_color or GOLD_LIGHT
        c = cut
        # Top-Left Bracket
        pygame.draw.line(surface, b_col, (rect.left + c, rect.top), (rect.left + c + 8, rect.top), 2)
        pygame.draw.line(surface, b_col, (rect.left, rect.top + c), (rect.left, rect.top + c + 8), 2)
        # Top-Right Bracket
        pygame.draw.line(surface, b_col, (rect.right - c, rect.top), (rect.right - c - 8, rect.top), 2)
        pygame.draw.line(surface, b_col, (rect.right, rect.top + c), (rect.right, rect.top + c + 8), 2)
        # Bottom-Left Bracket
        pygame.draw.line(surface, b_col, (rect.left + c, rect.bottom), (rect.left + c + 8, rect.bottom), 2)
        pygame.draw.line(surface, b_col, (rect.left, rect.bottom - c), (rect.left, rect.bottom - c - 8), 2)
        # Bottom-Right Bracket
        pygame.draw.line(surface, b_col, (rect.right - c, rect.bottom), (rect.right - c - 8, rect.bottom), 2)
        pygame.draw.line(surface, b_col, (rect.right, rect.bottom - c), (rect.right, rect.bottom - c - 8), 2)

        # Metallic Corner Rivets
        pygame.draw.circle(surface, GOLD_DARK, (rect.left + c + 2, rect.top + c + 2), 2)
        pygame.draw.circle(surface, GOLD_DARK, (rect.right - c - 2, rect.top + c + 2), 2)
        pygame.draw.circle(surface, GOLD_DARK, (rect.left + c + 2, rect.bottom - c - 2), 2)
        pygame.draw.circle(surface, GOLD_DARK, (rect.right - c - 2, rect.bottom - c - 2), 2)

def draw_ribbon_badge(
    surface: pygame.Surface,
    rect: pygame.Rect,
    text: str,
    bg_color: Tuple[int, int, int] = WOOD_BROWN,
    border_color: Tuple[int, int, int] = GOLD,
    text_color: Tuple[int, int, int] = WHITE,
    font_size: int = 12
):
    """Draws a prominent chevron-notched heraldic ribbon header badge."""
    w, h = rect.width, rect.height
    x, y = rect.x, rect.y
    notch = 10

    # Chevron Points (indented left and right edges)
    pts = [
        (x, y),
        (x + w, y),
        (x + w - notch, y + h // 2),
        (x + w, y + h),
        (x, y + h),
        (x + notch, y + h // 2)
    ]
    pygame.draw.polygon(surface, bg_color, pts)
    pygame.draw.polygon(surface, border_color, pts, width=2)

    font = get_font(font_size, bold=True)
    t_surf = font.render(text, True, text_color)
    surface.blit(t_surf, t_surf.get_rect(center=rect.center))

def draw_hex_badge(
    surface: pygame.Surface,
    center: Tuple[int, int],
    radius: int,
    bg_color: Tuple[int, int, int],
    border_color: Tuple[int, int, int] = GOLD,
    icon_or_text: str = "",
    text_color: Tuple[int, int, int] = WHITE,
    font_size: int = 12
):
    """Draws a crisp regular hexagon status emblem."""
    cx, cy = center
    pts = []
    for i in range(6):
        angle = math.radians(60 * i - 30)
        px = cx + radius * math.cos(angle)
        py = cy + radius * math.sin(angle)
        pts.append((px, py))

    pygame.draw.polygon(surface, bg_color, pts)
    pygame.draw.polygon(surface, border_color, pts, width=2)

    if icon_or_text:
        font = get_font(font_size, bold=True)
        txt_surf = font.render(icon_or_text, True, text_color)
        surface.blit(txt_surf, txt_surf.get_rect(center=center))

def wrap_text_fully(text: str, font: pygame.font.Font, max_width: int) -> List[str]:
    """Robust full text wrapping that preserves all words and never cuts off definitions."""
    if not text:
        return []
    words = text.split(" ")
    lines = []
    cur_line: List[str] = []

    for word in words:
        test_line = " ".join(cur_line + [word])
        if font.size(test_line)[0] <= max_width:
            cur_line.append(word)
        else:
            if cur_line:
                lines.append(" ".join(cur_line))
            cur_line = [word]

    if cur_line:
        lines.append(" ".join(cur_line))

    return lines

def draw_text_block(
    surface: pygame.Surface,
    rect: pygame.Rect,
    text: str,
    font: pygame.font.Font,
    color: Tuple[int, int, int] = WHITE,
    line_spacing: int = 4,
    shadow: bool = True
) -> int:
    """Draws multi-line text wrapped within rect with guaranteed zero overlap.
    Returns the total vertical height rendered.
    """
    lines = wrap_text_fully(text, font, rect.width)
    line_height = font.get_linesize() + line_spacing
    cur_y = rect.y

    for line in lines:
        if cur_y + font.get_linesize() > rect.bottom:
            break
        if shadow:
            s_surf = font.render(line, True, (10, 8, 6))
            surface.blit(s_surf, (rect.x + 1, cur_y + 1))
        t_surf = font.render(line, True, color)
        surface.blit(t_surf, (rect.x, cur_y))
        cur_y += line_height

    return cur_y - rect.y

