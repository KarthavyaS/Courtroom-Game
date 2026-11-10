"""PySide6 Desktop Application Entry Point for LOGIC COURTROOM.
Initializes the Qt Application, applies the Victorian Noir QSS stylesheet,
configures high-DPI scaling, and launches the desktop courtroom experience.
"""

import sys
import os

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import QApplication

from app_qt.styles import COURTROOM_QSS
from app_qt.config import get_qt_font
from app_qt.services.sound_service_qt import get_sound_service_qt
from app_qt.main_window import MainWindow


def main():
    # 1. High DPI Attributes & Quiet Multimedia Logging
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    os.environ["QT_LOGGING_RULES"] = "qt.multimedia*=false;qt.multimedia.ffmpeg*=false"

    app = QApplication(sys.argv)
    app.setApplicationName("LogicCourtroom")
    app.setOrganizationName("LogicCourtroom")

    # 2. Apply Custom Font & Dark Victorian Noir Stylesheet
    app.setFont(get_qt_font(10))
    app.setStyleSheet(COURTROOM_QSS)

    # 3. Initialize Audio Engine
    sound_service = get_sound_service_qt()

    # 4. Instantiate & Display Main Window
    window = MainWindow()
    window.show()

    # 5. Execute Event Loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

