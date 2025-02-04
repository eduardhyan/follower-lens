import json
import os
import pathlib
import time

from playwright.sync_api import BrowserContext, Page

import config


def get_cookies():
    out = []
    session_path = config.Session.get_file_path()
    if os.path.exists(session_path):
        out = json.loads(pathlib.Path(session_path).read_text())

    return out


def store_cookies(page: Page):
    cookies = page.context.cookies()

    session_path = config.Session.get_file_path()
    serialized_data = json.dumps(cookies)
    pathlib.Path(session_path).write_text(serialized_data)

    print("Stored latest cookies in session!")


def restore_cookies(context: BrowserContext):
    restored = False

    cookie_data = get_cookies()
    if len(cookie_data) > 0:
        print("Cookies added!")
        context.add_cookies(cookie_data)
        restored = True

    return restored


def validate_auth_configs():
    if not config.Account.password:
        raise Exception("Password not found in environment variables")


def manual_login(page: Page, persist_session=True):
    validate_auth_configs()

    btn = page.get_by_text("Allow all cookies")
    btn.click()

    # Fill credentials
    username_input = page.get_by_label("Phone number, username, or email")
    username_input.fill(config.Account.email)

    pwd_input = page.get_by_label("Password")
    pwd_input.fill(config.Account.password)

    # Hit the submit button to log in.
    submit_btn = page.locator("css=#loginForm [type=submit]")
    submit_btn.click()

    time.sleep(5)

    if persist_session:
        store_cookies(page)
