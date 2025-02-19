import hashlib
import json
import os
import pathlib


class Account:
    username = None
    email = None
    password = None
    is_public = None

    credentials_path = "cache/credentials.json"

    @staticmethod
    def get_encoded_username():
        result = hashlib.md5(Account.username.encode())
        return result.hexdigest()

    @staticmethod
    def init_credentials():
        out = None

        if os.path.exists(Account.credentials_path):
            out = json.loads(pathlib.Path(Account.credentials_path).read_text())

            Account.username = out.get("username", None)
            Account.email = out.get("email", None)
            Account.password = out.get("password", None)
            Account.is_public = out.get("is_public", None)

        # We have enough information if the account is public and the user name is captured
        # For private accounts we need email and password mandatory
        return (Account.username and Account.email and Account.password) or (
            Account.username and Account.is_public
        )

    @staticmethod
    def save_credentials(username: str, email: str, password: str, is_public: bool):
        Account.username = username
        Account.email = email
        Account.password = password
        Account.is_public = is_public

        pathlib.Path(Account.credentials_path).write_text(
            json.dumps(
                {
                    "username": username,
                    "email": email,
                    "password": password,
                    "is_public": is_public,
                }
            )
        )


class Session:
    base_path = "sessions"

    @staticmethod
    def get_file_path():
        return f"{Session.base_path}/{Account.get_encoded_username()}.json"
