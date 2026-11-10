"""Configuration settings, dimensions, colors, and font managers for PySide6 LOGIC COURTROOM.
"""

from pathlib import Path
from PySide6.QtGui import QColor, QFont

# Directory paths
APP_DIR = Path(__file__).resolve().parent
BASE_DIR = APP_DIR.parent
ASSETS_DIR = BASE_DIR / "assets"
DATA_DIR = BASE_DIR / "data"
SOUNDS_DIR = ASSETS_DIR / "sounds"

# Window settings (centered 1100 x 680 default, resizable)
DEFAULT_WIDTH = 1100
DEFAULT_HEIGHT = 680
SCREEN_WIDTH = DEFAULT_WIDTH
SCREEN_HEIGHT = DEFAULT_HEIGHT
GAME_TITLE = "LOGIC COURTROOM"
TAGLINE = "Where Logic Decides the Verdict"

# Hex color constants for QSS styling
HEX_BG_CHAMBER = "#140d0a"
HEX_BG_PANEL = "#221610"
HEX_BG_PANEL_ALT = "#2a1b14"
HEX_WOOD_BROWN = "#7d4b28"
HEX_WOOD_HOVER = "#9a5d32"
HEX_GOLD = "#ffd741"
HEX_GOLD_LIGHT = "#ffeb82"
HEX_GOLD_DARK = "#b48732"
HEX_LIGHT_PARCHMENT = "#f5ebd7"
HEX_MUTED_TEXT = "#c8b9aa"
HEX_BORDER = "#704222"
HEX_BORDER_GOLD = "#ffd741"

HEX_ACCENT_GREEN = "#2db955"
HEX_ACCENT_RED = "#eb3732"
HEX_ACCENT_BLUE = "#3796f5"
HEX_ACCENT_ORANGE = "#f58c23"
HEX_ACCENT_PURPLE = "#af55d7"

# QColor constants for QPainter vector drawings
COLOR_BG_CHAMBER = QColor(20, 13, 10)
COLOR_BG_PANEL = QColor(34, 22, 16)
COLOR_BG_CARD = COLOR_BG_PANEL
COLOR_BORDER = QColor(112, 66, 34)
COLOR_WOOD_BROWN = QColor(125, 75, 40)
COLOR_GOLD = QColor(255, 215, 65)
COLOR_GOLD_LIGHT = QColor(255, 235, 130)
COLOR_GOLD_DARK = QColor(180, 135, 50)
COLOR_LIGHT_PARCHMENT = QColor(245, 235, 215)
COLOR_TEXT_PARCHMENT = COLOR_LIGHT_PARCHMENT
COLOR_WHITE = QColor(255, 255, 255)
COLOR_MUTED_TEXT = QColor(200, 185, 170)
COLOR_TEXT_MUTED = COLOR_MUTED_TEXT

COLOR_ACCENT_GREEN = QColor(45, 185, 85)
COLOR_ACCENT_RED = QColor(235, 55, 50)
COLOR_ACCENT_BLUE = QColor(55, 150, 245)
COLOR_ACCENT_ORANGE = QColor(245, 140, 35)
COLOR_ACCENT_PURPLE = QColor(175, 85, 215)

_FONT_CACHE = {}

def get_qt_font(point_size: int = 12, bold: bool = False, italic: bool = False, family: str = "Segoe UI") -> QFont:
    """Returns a cached QFont with fallback typefaces."""
    key = (family, point_size, bold, italic)
    if key in _FONT_CACHE:
        return _FONT_CACHE[key]

    font = QFont(family, point_size)
    font.setBold(bold)
    font.setItalic(italic)
    font.setStyleHint(QFont.StyleHint.SansSerif)
    _FONT_CACHE[key] = font
    return font
