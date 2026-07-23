import sys
import os
import traceback
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from src.frontend.windows.main_window import MainWindow
from src.frontend.styles.theme import GITHUB_DARK_QSS


def resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


def excepthook(exc_type, exc_value, exc_tb):
    with open('crash.log', 'w', encoding='utf-8') as f:
        traceback.print_exception(exc_type, exc_value, exc_tb, file=f)
    sys.__excepthook__(exc_type, exc_value, exc_tb)


sys.excepthook = excepthook


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(GITHUB_DARK_QSS)

    icon_path = resource_path('icon.ico')
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
