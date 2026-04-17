import sys
from PySide6.QtWidgets import QApplication
from database import init_db
from gui_login import LoginWindow

def main():
    init_db()

    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()