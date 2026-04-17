from PySide6.QtWidgets import *
from PySide6.QtCore import Qt
from datetime import datetime
from database import get_connection
from vault_crypto import VaultCrypto
from hash_utils import HashUtils
from hash_cracker import BruteForceWorker, DictionaryWorker, RainbowWorker


class DashboardWindow(QWidget):
    def __init__(self, username, password, salt):
        super().__init__()

        self.username = username
        self.password = password
        self.salt = salt
        self.key = VaultCrypto.derive_key(password, salt)

        self.setWindowTitle("Dr.Vault - Dashboard")
        self.resize(1100, 700)

        main_layout = QHBoxLayout(self)

        # Sidebar
        sidebar = QFrame()
        sidebar.setFixedWidth(220)
        side_layout = QVBoxLayout(sidebar)

        self.home_btn = QPushButton("🏠 Home")
        self.vault_btn = QPushButton("🔐 Vault")
        self.hashlab_btn = QPushButton("🧪 Hash Lab")
        self.logout_btn = QPushButton("🚪 Logout")

        side_layout.addWidget(self.home_btn)
        side_layout.addWidget(self.vault_btn)
        side_layout.addWidget(self.hashlab_btn)
        side_layout.addStretch()
        side_layout.addWidget(self.logout_btn)

        # Stack
        self.stack = QStackedWidget()
        self.home_page = self.build_home()
        self.vault_page = self.build_vault()
        self.hashlab_page = self.build_hashlab()

        self.stack.addWidget(self.home_page)
        self.stack.addWidget(self.vault_page)
        self.stack.addWidget(self.hashlab_page)

        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.stack)

        self.home_btn.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        self.vault_btn.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        self.hashlab_btn.clicked.connect(lambda: self.stack.setCurrentIndex(2))
        self.logout_btn.clicked.connect(self.handle_logout)

        self.load_vault()

    # ================= LOGOUT =================
    def handle_logout(self):
        from gui_login import LoginWindow
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()

    # ================= HOME =================
    def build_home(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        text = QTextEdit()
        text.setReadOnly(True)
        text.setText("Dr. Vault - Homepage\n\n\nThis is a application that functions as a Secure password storage and management tool using AES encryption and decryption.\n\nThis application also has a basic hash lab that showcases different tools- hasher and encoder, password strength meter, basic password cracker.\n\nPlease enjoy your visit.")

        layout.addWidget(text)
        return page

    # ================= VAULT =================
    def build_vault(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        btn_layout = QHBoxLayout()

        self.add_btn = QPushButton("Add")
        self.view_btn = QPushButton("View")
        self.delete_btn = QPushButton("Delete")

        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.view_btn)
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addStretch()

        self.add_btn.clicked.connect(self.add_entry)
        self.view_btn.clicked.connect(self.view_entry)
        self.delete_btn.clicked.connect(self.delete_entry)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Website", "Username", "Created"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        layout.addLayout(btn_layout)
        layout.addWidget(self.table)

        return page

    def load_vault(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT website, username, created_at FROM vault WHERE owner=?", (self.username,))
        rows = cur.fetchall()
        conn.close()

        self.table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            for c, value in enumerate(row):
                self.table.setItem(r, c, QTableWidgetItem(str(value)))

    def add_entry(self):
        site, ok = QInputDialog.getText(self, "Website", "Enter website:")
        if not ok or not site:
            return

        user, ok = QInputDialog.getText(self, "Username", "Enter username:")
        if not ok or not user:
            return

        pwd, ok = QInputDialog.getText(self, "Password", "Enter password:")
        if not ok or not pwd:
            return

        encrypted = VaultCrypto.encrypt(self.key, pwd)

        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO vault(owner,website,username,password_encrypted,created_at) VALUES(?,?,?,?,?)",
            (self.username, site, user, encrypted, datetime.now().strftime("%Y-%m-%d"))
        )
        conn.commit()
        conn.close()

        self.load_vault()

    def view_entry(self):
        row = self.table.currentRow()
        if row == -1:
            return

        site = self.table.item(row, 0).text()

        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT password_encrypted FROM vault WHERE owner=? AND website=?",
            (self.username, site)
        )
        result = cur.fetchone()
        conn.close()

        if result:
            decrypted = VaultCrypto.decrypt(self.key, result[0])
            QMessageBox.information(self, "Decrypted Password", decrypted)

    def delete_entry(self):
        row = self.table.currentRow()
        if row == -1:
            return

        site = self.table.item(row, 0).text()

        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "DELETE FROM vault WHERE owner=? AND website=?",
            (self.username, site)
        )
        conn.commit()
        conn.close()

        self.load_vault()

    # ================= HASH LAB =================
    def build_hashlab(self):
        tabs = QTabWidget()
        tabs.addTab(self.build_hash_generator_tab(), "Hash Generator")
        tabs.addTab(self.build_strength_tab(), "Strength Analyzer")
        tabs.addTab(self.build_bruteforce_tab(), "Brute Force")
        tabs.addTab(self.build_dictionary_tab(), "Dictionary Attack")
        tabs.addTab(self.build_rainbow_tab(), "Rainbow Table")
        return tabs

    # -------- Hash Generator --------
    def build_hash_generator_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.hash_input = QLineEdit()
        self.hash_algo = QComboBox()
        self.hash_algo.addItems(["SHA-256", "SHA-512", "MD5", "bcrypt", "Base64 Encode", "Base64 Decode"])

        self.hash_output = QTextEdit()
        self.hash_output.setReadOnly(True)

        btn = QPushButton("Generate")
        btn.clicked.connect(self.run_hash)

        layout.addWidget(self.hash_input)
        layout.addWidget(self.hash_algo)
        layout.addWidget(btn)
        layout.addWidget(self.hash_output)
        return tab

    def run_hash(self):
        result = HashUtils.generate_hash(self.hash_input.text(), self.hash_algo.currentText())
        self.hash_output.setText(result)

    # -------- Strength --------
    def build_strength_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.strength_input = QLineEdit()
        self.strength_output = QTextEdit()
        self.strength_output.setReadOnly(True)

        btn = QPushButton("Analyze")
        btn.clicked.connect(self.run_strength)

        layout.addWidget(self.strength_input)
        layout.addWidget(btn)
        layout.addWidget(self.strength_output)
        return tab

    def run_strength(self):
        result = HashUtils.password_strength(self.strength_input.text())
        self.strength_output.setText(result)

    # -------- Brute Force --------
    def build_bruteforce_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.bf_input = QLineEdit()
        self.bf_algo = QComboBox()
        self.bf_algo.addItems(["SHA-256", "SHA-512", "MD5"])

        self.bf_progress = QProgressBar()
        self.bf_output = QLineEdit()

        start = QPushButton("Start")
        stop = QPushButton("Stop")
        start.clicked.connect(self.start_bf)
        stop.clicked.connect(self.stop_bf)

        layout.addWidget(self.bf_input)
        layout.addWidget(self.bf_algo)
        layout.addWidget(start)
        layout.addWidget(stop)
        layout.addWidget(self.bf_progress)
        layout.addWidget(self.bf_output)
        return tab

    def start_bf(self):
        self.bf_worker = BruteForceWorker(self.bf_input.text(), self.bf_algo.currentText())
        self.bf_worker.progress.connect(self.bf_progress.setValue)
        self.bf_worker.found.connect(self.bf_output.setText)
        self.bf_worker.start()

    def stop_bf(self):
        if hasattr(self, "bf_worker"):
            self.bf_worker.stop()

    # -------- Dictionary Attack --------
    def build_dictionary_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.dict_input = QLineEdit()
        self.dict_input.setPlaceholderText("Target hash")

        self.dict_file_btn = QPushButton("Load Wordlist")
        self.dict_file_btn.clicked.connect(self.load_wordlist)

        self.dict_progress = QProgressBar()
        self.dict_output = QLineEdit()

        start = QPushButton("Start")
        stop = QPushButton("Stop")
        start.clicked.connect(self.start_dict)
        stop.clicked.connect(self.stop_dict)

        layout.addWidget(self.dict_input)
        layout.addWidget(self.dict_file_btn)
        layout.addWidget(start)
        layout.addWidget(stop)
        layout.addWidget(self.dict_progress)
        layout.addWidget(self.dict_output)
        return tab

    def load_wordlist(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select Wordlist")
        if file:
            self.wordlist_path = file
            self.dict_file_btn.setText(file.split("/")[-1])

    def start_dict(self):
        if not hasattr(self, "wordlist_path"):
            QMessageBox.warning(self, "Error", "Load a wordlist first")
            return

        self.dict_worker = DictionaryWorker(self.dict_input.text(), "SHA-256", self.wordlist_path)
        self.dict_worker.progress.connect(self.dict_progress.setValue)
        self.dict_worker.found.connect(self.dict_output.setText)
        self.dict_worker.start()

    def stop_dict(self):
        if hasattr(self, "dict_worker"):
            self.dict_worker.stop()

    # -------- Rainbow Table --------
    def build_rainbow_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.rainbow_input = QLineEdit()
        self.rainbow_input.setPlaceholderText("Target hash")

        self.rainbow_file_btn = QPushButton("Load Rainbow Table")
        self.rainbow_file_btn.clicked.connect(self.load_rainbow)

        self.rainbow_progress = QProgressBar()
        self.rainbow_output = QLineEdit()

        start = QPushButton("Start")
        stop = QPushButton("Stop")
        start.clicked.connect(self.start_rainbow)
        stop.clicked.connect(self.stop_rainbow)

        layout.addWidget(self.rainbow_input)
        layout.addWidget(self.rainbow_file_btn)
        layout.addWidget(start)
        layout.addWidget(stop)
        layout.addWidget(self.rainbow_progress)
        layout.addWidget(self.rainbow_output)
        return tab

    def load_rainbow(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select Rainbow Table")
        if file:
            self.rainbow_file = file
            self.rainbow_file_btn.setText(file.split("/")[-1])

    def start_rainbow(self):
        if not hasattr(self, "rainbow_file"):
            QMessageBox.warning(self, "Error", "Load rainbow table first")
            return

        self.rainbow_worker = RainbowWorker(self.rainbow_input.text(), self.rainbow_file)
        self.rainbow_worker.progress.connect(self.rainbow_progress.setValue)
        self.rainbow_worker.found.connect(self.rainbow_output.setText)
        self.rainbow_worker.start()

    def stop_rainbow(self):
        if hasattr(self, "rainbow_worker"):
            self.rainbow_worker.stop()