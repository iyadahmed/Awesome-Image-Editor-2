import sys

from .app import Application
from .mainwindow import MainWindow


def main():
    app = Application(sys.argv)
    main_window = MainWindow()
    exit_code = app.exec()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
