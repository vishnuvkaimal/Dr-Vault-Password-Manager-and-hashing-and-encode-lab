from PySide6.QtCore import QThread, Signal
import hashlib
import itertools
import time
import os


# =========================
# SHARED HASH FUNCTION
# =========================
def compute_hash(text, algorithm):
    if algorithm == "SHA-256":
        return hashlib.sha256(text.encode()).hexdigest()
    elif algorithm == "SHA-512":
        return hashlib.sha512(text.encode()).hexdigest()
    elif algorithm == "MD5":
        return hashlib.md5(text.encode()).hexdigest()
    else:
        return ""


# =========================
# BRUTE FORCE WORKER
# =========================
class BruteForceWorker(QThread):
    progress = Signal(int)
    found = Signal(str)
    finished = Signal()

    def __init__(self, target_hash, algorithm, max_length=3):
        super().__init__()
        self.target_hash = target_hash
        self.algorithm = algorithm
        self.max_length = max_length
        self._running = True
        self.charset = "abc123"

    def run(self):
        total = sum(len(self.charset) ** i for i in range(1, self.max_length + 1))
        count = 0

        for length in range(1, self.max_length + 1):
            if not self._running:
                break

            for combo in itertools.product(self.charset, repeat=length):
                if not self._running:
                    break

                guess = ''.join(combo)
                hashed_guess = compute_hash(guess, self.algorithm)
                count += 1

                percent = int((count / total) * 100)
                self.progress.emit(percent)

                if hashed_guess == self.target_hash:
                    self.found.emit(guess)
                    self.finished.emit()
                    return

        self.finished.emit()

    def stop(self):
        self._running = False


# =========================
# DICTIONARY WORKER (FILE-BASED)
# =========================
class DictionaryWorker(QThread):
    progress = Signal(int)
    found = Signal(str)
    finished = Signal()

    def __init__(self, target_hash, algorithm, wordlist_path):
        super().__init__()
        self.target_hash = target_hash
        self.algorithm = algorithm
        self.wordlist_path = wordlist_path
        self._running = True

    def run(self):
        if not os.path.exists(self.wordlist_path):
            self.finished.emit()
            return

        with open(self.wordlist_path, "r", encoding="utf-8", errors="ignore") as f:
            words = f.readlines()

        total = len(words)

        for i, word in enumerate(words, start=1):
            if not self._running:
                break

            word = word.strip()
            hashed_word = compute_hash(word, self.algorithm)

            percent = int((i / total) * 100)
            self.progress.emit(percent)

            if hashed_word == self.target_hash:
                self.found.emit(word)
                self.finished.emit()
                return

        self.finished.emit()

    def stop(self):
        self._running = False


# =========================
# RAINBOW TABLE WORKER
# =========================
class RainbowWorker(QThread):
    progress = Signal(int)
    found = Signal(str)
    finished = Signal()

    def __init__(self, target_hash, rainbow_file):
        super().__init__()
        self.target_hash = target_hash
        self.rainbow_file = rainbow_file
        self._running = True

    def run(self):
        if not os.path.exists(self.rainbow_file):
            self.finished.emit()
            return

        with open(self.rainbow_file, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()

        total = len(lines)

        for i, line in enumerate(lines, start=1):
            if not self._running:
                break

            line = line.strip()
            if ":" not in line:
                continue

            plain, hashed = line.split(":", 1)

            percent = int((i / total) * 100)
            self.progress.emit(percent)

            if hashed == self.target_hash:
                self.found.emit(plain)
                self.finished.emit()
                return

        self.finished.emit()

    def stop(self):
        self._running = False