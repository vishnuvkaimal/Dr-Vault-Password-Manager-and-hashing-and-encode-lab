from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
import base64
import os

class VaultCrypto:
    @staticmethod
    def derive_key(password, salt):
        return PBKDF2(password, salt, dkLen=32)

    @staticmethod
    def encrypt(key, plaintext):
        cipher = AES.new(key, AES.MODE_GCM)
        ciphertext, tag = cipher.encrypt_and_digest(plaintext.encode())
        return base64.b64encode(cipher.nonce + tag + ciphertext)

    @staticmethod
    def decrypt(key, ciphertext_b64):
        raw = base64.b64decode(ciphertext_b64)
        nonce, tag, ciphertext = raw[:16], raw[16:32], raw[32:]
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        return cipher.decrypt_and_verify(ciphertext, tag).decode()