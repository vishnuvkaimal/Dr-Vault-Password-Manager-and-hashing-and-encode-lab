from PySide6.QtWidgets import (
    QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QMessageBox
)
from auth import signup, login
from gui_dashboard import DashboardWindow

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dr. Vault - Login")
        self.resize(600, 400)

        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(40, 40, 40, 40)

        title = QLabel("Dr. Vault Login")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        layout.addWidget(QLabel("Username"))
        self.username_input = QLineEdit()
        layout.addWidget(self.username_input)

        layout.addWidget(QLabel("Password"))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        self.signup_btn = QPushButton("Signup")
        self.login_btn = QPushButton("Login")
        layout.addWidget(self.signup_btn)
        layout.addWidget(self.login_btn)

        layout.addStretch()
        self.setLayout(layout)

        self.signup_btn.clicked.connect(self.handle_signup)
        self.login_btn.clicked.connect(self.handle_login)

    def handle_signup(self):
        u = self.username_input.text()
        p = self.password_input.text()
        if not u or not p:
            QMessageBox.warning(self, "Error", "Enter username and password")
            return
        if signup(u, p):
            QMessageBox.information(self, "Success", "User created")
        else:
            QMessageBox.warning(self, "Error", "User already exists")

    def handle_login(self):
        u = self.username_input.text()
        p = self.password_input.text()
        success, salt = login(u, p)
        if success:
            self.dashboard = DashboardWindow(u, p, salt)
            self.dashboard.show()
            self.close()
        else:
            QMessageBox.warning(self, "Error", "Invalid credentials")