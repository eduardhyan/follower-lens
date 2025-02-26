"""
This module provides utility functions for managing session paths.
"""


def get_session_path(account) -> str:
    """
    Generate the session file path for the given account.

    Args:
        account: An instance of the Account class.

    Returns:
        str: The session file path.
    """
    return f"sessions/{account.get_encoded_username()}.json"
