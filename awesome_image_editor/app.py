import ctypes
import platform
from pathlib import PurePath
from typing import List

from PyQt6.QtCore import QCoreApplication
from PyQt6.QtGui import QColor, QIcon, QPalette
from PyQt6.QtWidgets import QApplication

__all__ = ("Application",)


class Application(QApplication):
    def __init__(self, argv: List[str]):
        super().__init__(argv)

        # Fixes app icon not displayed in Windows taskbar
        if platform.system() == "Windows":
            appid = "iyadahmed.AwesomeImageEditor"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appid)  # type: ignore

        QCoreApplication.setApplicationName("Awesome Image Editor")
        QCoreApplication.setOrganizationName("Iyad Ahmed")
        QCoreApplication.setApplicationVersion("0.0.1")

        self.setWindowIcon(
            QIcon((PurePath(__file__).parent / "icons" / "app2.svg").as_posix())
        )
        # Dark theme
        # https://stackoverflow.com/a/56851493/8094047
        self.setStyle("Fusion")
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(175,175,175))
        palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(167,0,72))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(175,175,175))
        palette.setColor(QPalette.ColorRole.Text, QColor(175,175,175))
        palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(175,175,175))
        palette.setColor(QPalette.ColorRole.BrightText, QColor("white"))
        palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(56, 20, 35))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(167,0,72))
        self.setPalette(palette)
