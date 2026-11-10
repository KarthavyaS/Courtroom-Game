"""Configuration settings, dimensions, colors, and mystery font managers for LOGIC COURTROOM.
"""

import os
from pathlib import Path
import pygame

# Center the Pygame window on the laptop/desktop screen
os.environ["SDL_VIDEO_CENTERED"] = "1"

# Base directory paths
BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
DATA_DIR = BASE_DIR / "data"

# Window settings - 1100 x 680 compact centered desktop window
SCREEN_WIDTH = 1100
SCREEN_HEIGHT = 680
FPS = 60
GAME_TITLE = "LOGIC COURTROOM"
TAGLINE = "Where Logic Decides the Verdict"

# Color Palette - High-Contrast Vibrant Vintage Courtroom & Detective Theme
BACKGROUND = (22, 16, 13)           # Deep Rich Walnut / Courtroom Chamber
DARK_BROWN = (38, 26, 20)           # Mahogany Panel Base
WOOD_BROWN = (125, 75, 40)          # Warm Rich Cedar Wood
LIGHT_PARCHMENT = (245, 235, 215)   # Crisp Light Ivory (High Contrast on dark backgrounds)
GOLD = (255, 215, 65)               # Vibrant Royal Gold
GOLD_LIGHT = (255, 235, 130)        # Bright Luminous Gold
GOLD_DARK = (180, 135, 50)          # Shadow Amber Gold
WHITE = (255, 255, 255)             # Pure Crisp White
BLACK = (10, 8, 6)                  # Pitch Shadow Black
MUTED_TEXT = (200, 185, 170)        # Clean Soft Silver-Cream (High Contrast secondary text)
CARD_BG = (34, 25, 20)              # Rich Deep Panel Background
CARD_BORDER = (215, 170, 85)        # Brass Gold Border

# Vibrant Accent status colors
ACCENT_GREEN = (45, 185, 85)        # Vibrant Emerald (Supported / Valid / Collected)
ACCENT_RED = (235, 55, 50)          # Vibrant Crimson (Contradicted / Guilt / Danger)
ACCENT_BLUE = (55, 150, 245)        # Vibrant Azure Blue (Digital / Evidence / Information)
ACCENT_ORANGE = (245, 140, 35)      # Vibrant Amber (Warning / Circumstantial)
ACCENT_PURPLE = (175, 85, 215)      # Vibrant Amethyst (Digital / Forensics)
OVERLAY_DARK = (0, 0, 0, 180)

# Fonts helper
_FONT_CACHE = {}

def get_font(size_or_name=16, size: int = None, bold: bool = False, italic: bool = False) -> pygame.font.Font:
    """Safely retrieves a cached crisp modern game font supporting polymorphic arguments:
    Examples:
        get_font(16) -> 16pt Game Font
        get_font(14, bold=True) -> 14pt Bold Game Font
        get_font("Trebuchet MS", 18) -> 18pt Trebuchet MS
    """
    if isinstance(size_or_name, int):
        font_size = size_or_name
        font_family = "Trebuchet MS"
    elif isinstance(size_or_name, str):
        if size is not None:
            font_size = size
            font_family = size_or_name
        else:
            font_size = 16
            font_family = size_or_name
    else:
        font_size = 16
        font_family = "Trebuchet MS"

    # Enforce minimum readable font size for crisp legibility
    font_size = max(12, font_size)

    key = (font_family, font_size, bold, italic)
    if key in _FONT_CACHE:
        return _FONT_CACHE[key]

    if not pygame.font.get_init():
        pygame.font.init()

    # Prioritize punchy, high-legibility game & legal typefaces
    candidate_fonts = [
        font_family,
        "Trebuchet MS",
        "Segoe UI",
        "Verdana",
        "Franklin Gothic Medium",
        "Century Gothic",
        "Arial",
        "Palatino Linotype",
        "Constantia",
        "Georgia",
        "sans-serif"
    ]

    font_obj = None
    for candidate in candidate_fonts:
        try:
            font_obj = pygame.font.SysFont(candidate, font_size, bold=bold, italic=italic)
            if font_obj:
                break
        except Exception:
            continue

    if font_obj is None:
        font_obj = pygame.font.Font(None, font_size)

    _FONT_CACHE[key] = font_obj
    return font_obj

