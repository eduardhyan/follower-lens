"""
This module provides utility functions for encryption and decryption
using the Fernet symmetric encryption method from the cryptography library.
"""

import os

from cryptography.fernet import Fernet

import constants


def load_key() -> bytes:
    """Load or generate an encryption key."""
    key_path = constants.ENCRYPTION_KEY_PATH

    if os.path.exists(key_path):
        with open(key_path, "rb") as key_file:
            return key_file.read()
    else:
        key = Fernet.generate_key()
        with open(key_path, "wb") as key_file:
            key_file.write(key)
        return key


def encrypt(data: str, key: bytes) -> str:
    """Encrypt the given data."""
    cipher = Fernet(key)
    return cipher.encrypt(data.encode()).decode()


def decrypt(data: str, key: bytes) -> str:
    """Decrypt the given data."""
    cipher = Fernet(key)
    return cipher.decrypt(data.encode()).decode()
