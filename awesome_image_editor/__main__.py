import sys
import os
import platform

# Force use of X11 Qt plugin on Linux to avoid issues with moving QDockWidget and QToolBar on Wayland
# https://github.com/KDAB/KDDockWidgets/issues/10
if platform.system() == "Linux":
    os.environ["QT_QPA_PLATFORM"] = "xcb"

from .app import Application
from .mainwindow import MainWindow


def main():
    app = Application(sys.argv)
    main_window = MainWindow()
    exit_code = app.exec()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
