import hashlib
import bcrypt
import base64
import re

class HashUtils:
    @staticmethod
    def generate_hash(text, algorithm):
        text = text.encode()
        if algorithm == "SHA-256":
            return hashlib.sha256(text).hexdigest()
        elif algorithm == "SHA-512":
            return hashlib.sha512(text).hexdigest()
        elif algorithm == "MD5":
            return hashlib.md5(text).hexdigest()
        elif algorithm == "bcrypt":
            return bcrypt.hashpw(text, bcrypt.gensalt()).decode()
        elif algorithm == "Base64 Encode":
            return base64.b64encode(text).decode()
        elif algorithm == "Base64 Decode":
            return base64.b64decode(text).decode()
        else:
            return ""
    
    @staticmethod
    def password_strength(password):
        length = len(password)
        lower = bool(re.search(r"[a-z]", password))
        upper = bool(re.search(r"[A-Z]", password))
        digit = bool(re.search(r"[0-9]", password))
        special = bool(re.search(r"[^a-zA-Z0-9]", password))

        score = sum([lower, upper, digit, special])
        if length >= 12 and score == 4:
            return "Very Strong"
        elif length >= 8 and score >= 3:
            return "Strong"
        elif length >= 6:
            return "Medium"
        else:
            return "Weak"