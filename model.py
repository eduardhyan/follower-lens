"""
This module defines the Account class for managing user credentials.
It provides methods to load, save, and encode user credentials.
"""

import hashlib
import json
import os
from typing import Optional

import constants
from utils.encryption_utils import decrypt, encrypt, load_key


class Account:
    """
    A class to manage user credentials.

    Attributes:
        username (Optional[str]): The username of the account.
        email (Optional[str]): The email of the account.
        password (Optional[str]): The password of the account.
        credentials_path (str): The path to the credentials file.
    """

    def __init__(self, credentials_path: str = constants.CREDENTIALS_PATH):
        self.username: Optional[str] = None
        self.email: Optional[str] = None
        self.password: Optional[str] = None
        self.credentials_path = credentials_path
        self.key = load_key()

    def load_credentials(self) -> bool:
        """Load credentials from the credentials file."""
        if not os.path.exists(self.credentials_path):
            print(f"Warning: Credentials file does not exist: {self.credentials_path}")
            return False

        try:
            with open(self.credentials_path, "r", encoding="utf-8") as file:
                contents = file.read()
                data = decrypt(contents, self.key)
                data = json.loads(data)

                self.username = data.get("username")
                self.email = data.get("email")
                self.password = data.get("password")
                print("Info: Credentials loaded successfully.")
        except (OSError, json.JSONDecodeError) as e:
            print(f"Error: Failed to load credentials: {e}")
            return False

        return bool(self.username and self.email and self.password)

    def save_credentials(self, username: str, email: str, password: str) -> None:
        """Save credentials to the credentials file."""
        self.username = username
        self.email = email
        self.password = password

        data = {
            "username": username,
            "email": email,
            "password": password,
        }

        try:
            with open(self.credentials_path, "w", encoding="utf-8") as file:
                contents = json.dumps(data)
                file.write(encrypt(contents, self.key))
                print("Info: Credentials saved successfully.")
        except OSError as e:
            print(f"Error: Failed to save credentials: {e}")

    def get_encoded_username(self) -> str:
        """Return the MD5 hash of the username."""
        if self.username is None:
            raise ValueError("Username is not set.")
        return hashlib.md5(self.username.encode()).hexdigest()
