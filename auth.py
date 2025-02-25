"""
This module provides authentication-related functions for the Follower Lens application.
It includes functions for managing cookies, validating authentication configurations,
and performing manual login.
"""

import json
import os
import pathlib
import time

from playwright.sync_api import BrowserContext, Page

import config


def get_cookies():
    """
    Retrieves cookies from the session file.

    Returns:
        list: A list of cookies.
    """
    out = []
    session_path = config.Session.get_file_path()
    if os.path.exists(session_path):
        out = json.loads(pathlib.Path(session_path).read_text())
    return out


def store_cookies(page: Page):
    """
    Stores cookies to the session file.

    Args:
        page (Page): The Playwright page object.
    """
    cookies = page.context.cookies()
    session_path = config.Session.get_file_path()
    serialized_data = json.dumps(cookies)
    pathlib.Path(session_path).write_text(serialized_data)
    print("Stored latest cookies in session!")


def restore_cookies(context: BrowserContext):
    """
    Restores cookies to the browser context.

    Args:
        context (BrowserContext): The Playwright browser context.

    Returns:
        bool: True if cookies were restored, False otherwise.
    """
    restored = False
    cookie_data = get_cookies()
    if len(cookie_data) > 0:
        print("Cookies added!")
        context.add_cookies(cookie_data)
        restored = True
    return restored


def validate_auth_configs():
    """
    Validates the authentication configurations.

    Raises:
        Exception: If the password or email is not found in the configurations.
    """
    if not config.Account.password:
        raise Exception("Password not found in configurations")
    if not config.Account.email:
        raise Exception("Email not found in configurations")


def manual_login(page: Page, persist_session=True):
    """
    Performs manual login and optionally stores the session cookies.

    Args:
        page (Page): The Playwright page object.
        persist_session (bool): Whether to store the session cookies after login.
    """
    validate_auth_configs()

    btn = page.get_by_text("Allow all cookies")
    if btn.count():
        btn.click()

    # Fill credentials
    username_input = page.get_by_label("Phone number, username, or email")
    username_input.fill(config.Account.email)

    pwd_input = page.get_by_label("Password")
    pwd_input.fill(config.Account.password)

    # Hit the submit button to log in.
    submit_btn = page.locator("css=#loginForm [type=submit]")
    submit_btn.click()

    page.wait_for_url("**/accounts/**")
    time.sleep(2)

    if persist_session:
        store_cookies(page)
