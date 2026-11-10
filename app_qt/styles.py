"""Victorian Noir Modern Dark Stylesheet (QSS) for PySide6 LOGIC COURTROOM.
"""

from app_qt.config import (
    HEX_BG_CHAMBER, HEX_BG_PANEL, HEX_BG_PANEL_ALT, HEX_WOOD_BROWN,
    HEX_WOOD_HOVER, HEX_GOLD, HEX_GOLD_LIGHT, HEX_GOLD_DARK,
    HEX_LIGHT_PARCHMENT, HEX_MUTED_TEXT, HEX_BORDER, HEX_BORDER_GOLD,
    HEX_ACCENT_GREEN, HEX_ACCENT_RED, HEX_ACCENT_BLUE, HEX_ACCENT_PURPLE
)

COURTROOM_QSS = f"""
/* Global Window & Widget Settings */
QMainWindow, QWidget#CentralWidget {{
    background-color: {HEX_BG_CHAMBER};
    color: {HEX_LIGHT_PARCHMENT};
    font-family: "Segoe UI", "Trebuchet MS", sans-serif;
    font-size: 13px;
}}

QWidget {{
    color: {HEX_LIGHT_PARCHMENT};
    font-family: "Segoe UI", "Trebuchet MS", sans-serif;
}}

/* Card Containers */
QFrame.court-card {{
    background-color: {HEX_BG_PANEL};
    border: 1px solid {HEX_BORDER};
    border-radius: 8px;
}}

QFrame.court-card-gold {{
    background-color: {HEX_BG_PANEL_ALT};
    border: 1px solid {HEX_GOLD};
    border-radius: 8px;
}}

QFrame.court-panel {{
    background-color: {HEX_BG_PANEL};
    border: 1px solid {HEX_BORDER};
    border-radius: 6px;
}}

QFrame.header-strip {{
    background-color: #2b180f;
    border-bottom: 2px solid {HEX_GOLD};
}}

/* Typography Classes */
QLabel {{
    color: {HEX_LIGHT_PARCHMENT};
}}

QLabel.title-gold {{
    color: {HEX_GOLD};
    font-size: 20px;
    font-weight: bold;
    letter-spacing: 1px;
}}

QLabel.section-header {{
    color: {HEX_GOLD_LIGHT};
    font-size: 14px;
    font-weight: bold;
    letter-spacing: 0.5px;
}}

QLabel.subtitle-parchment {{
    color: #e6dac3;
    font-size: 13px;
}}

QLabel.muted-label {{
    color: {HEX_MUTED_TEXT};
    font-size: 11px;
}}

/* Buttons */
QPushButton {{
    background-color: {HEX_WOOD_BROWN};
    color: #ffffff;
    border: 1px solid {HEX_GOLD_DARK};
    border-radius: 6px;
    padding: 7px 16px;
    font-weight: bold;
    font-size: 12px;
    min-height: 22px;
}}

QPushButton:hover {{
    background-color: {HEX_WOOD_HOVER};
    border: 1px solid {HEX_GOLD_LIGHT};
}}

QPushButton:pressed {{
    background-color: #4a2814;
    border: 1px solid {HEX_GOLD};
    padding-top: 9px;
}}

QPushButton:disabled {{
    background-color: #261912;
    color: #6e5e54;
    border: 1px solid #3c2a20;
}}

/* Specific Button Variants */
QPushButton.btn-gold {{
    background-color: #b37e19;
    border: 1px solid {HEX_GOLD_LIGHT};
    color: #ffffff;
}}

QPushButton.btn-gold:hover {{
    background-color: #d49520;
    border: 1px solid #ffffff;
}}

QPushButton.btn-success {{
    background-color: #238636;
    border: 1px solid {HEX_ACCENT_GREEN};
    color: #ffffff;
}}

QPushButton.btn-success:hover {{
    background-color: #2ea043;
    border: 1px solid #ffffff;
}}

QPushButton.btn-danger {{
    background-color: #a82723;
    border: 1px solid {HEX_ACCENT_RED};
    color: #ffffff;
}}

QPushButton.btn-danger:hover {{
    background-color: #cf332e;
    border: 1px solid #ffffff;
}}

QPushButton.btn-nav {{
    background-color: #291a13;
    border: 1px solid #633c22;
    padding: 5px 12px;
    font-size: 11px;
    border-radius: 5px;
}}

QPushButton.btn-nav:hover {{
    background-color: #553422;
    border: 1px solid {HEX_GOLD};
}}

QPushButton.btn-nav-active {{
    background-color: #965f23;
    border: 1px solid {HEX_GOLD};
    color: #ffffff;
    font-weight: bold;
}}

/* Text Inputs and Editors */
QLineEdit, QTextEdit, QPlainTextEdit {{
    background-color: #19100c;
    color: {HEX_LIGHT_PARCHMENT};
    border: 1px solid #6a3e20;
    border-radius: 6px;
    padding: 6px 10px;
    font-family: "Georgia", "Segoe UI", serif;
    font-size: 13px;
    selection-background-color: {HEX_GOLD};
    selection-color: {HEX_BG_CHAMBER};
}}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
    border: 1px solid {HEX_GOLD};
    background-color: #1e130e;
}}

/* Text Browser (Read-only dossier viewer) */
QTextBrowser {{
    background-color: #1a110c;
    color: {HEX_LIGHT_PARCHMENT};
    border: 1px solid #5a351c;
    border-radius: 6px;
    padding: 10px;
    font-size: 13px;
    line-height: 1.5;
}}

/* List Widgets (Cases, evidence, suspects) */
QListWidget {{
    background-color: #1a110c;
    color: {HEX_LIGHT_PARCHMENT};
    border: 1px solid #5a351c;
    border-radius: 6px;
    padding: 4px;
}}

QListWidget::item {{
    padding: 8px 10px;
    border-radius: 4px;
    margin-bottom: 3px;
}}

QListWidget::item:hover {{
    background-color: #3b2417;
    border: 1px solid #8c5a2e;
}}

QListWidget::item:selected {{
    background-color: #72401f;
    border: 1px solid {HEX_GOLD};
    color: #ffffff;
    font-weight: bold;
}}

/* Tabs */
QTabWidget::pane {{
    border: 1px solid #704222;
    background-color: {HEX_BG_PANEL};
    border-radius: 6px;
    top: -1px;
}}

QTabBar::tab {{
    background-color: #291a13;
    color: {HEX_MUTED_TEXT};
    border: 1px solid #55331e;
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    padding: 7px 16px;
    margin-right: 2px;
    font-weight: bold;
    font-size: 11px;
}}

QTabBar::tab:hover {{
    background-color: #4a2c1b;
    color: #ffffff;
}}

QTabBar::tab:selected {{
    background-color: {HEX_BG_PANEL};
    color: {HEX_GOLD};
    border: 1px solid #704222;
    border-bottom: 2px solid {HEX_BG_PANEL};
}}

/* Progress Bar */
QProgressBar {{
    background-color: #1a110c;
    border: 1px solid #633c22;
    border-radius: 5px;
    text-align: center;
    color: #ffffff;
    font-size: 11px;
    font-weight: bold;
    height: 16px;
}}

QProgressBar::chunk {{
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1f883d, stop:1 {HEX_ACCENT_GREEN});
    border-radius: 4px;
}}

/* Scrollbars */
QScrollBar:vertical {{
    background-color: #140d0a;
    width: 10px;
    margin: 0px;
    border-radius: 5px;
}}

QScrollBar::handle:vertical {{
    background-color: #4f2f1a;
    min-height: 25px;
    border-radius: 5px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: #7a4827;
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar:horizontal {{
    background-color: #140d0a;
    height: 10px;
    margin: 0px;
    border-radius: 5px;
}}

QScrollBar::handle:horizontal {{
    background-color: #4f2f1a;
    min-width: 25px;
    border-radius: 5px;
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0px;
}}

/* Splitters */
QSplitter::handle {{
    background-color: #442716;
}}

QSplitter::handle:hover {{
    background-color: {HEX_GOLD};
}}

/* Tooltips */
QToolTip {{
    background-color: #24160f;
    color: {HEX_GOLD_LIGHT};
    border: 1px solid {HEX_GOLD};
    padding: 6px 10px;
    border-radius: 4px;
    font-size: 11px;
}}
"""

