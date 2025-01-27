import time
import pickle
import os
from playwright.sync_api import sync_playwright, Playwright, Page, BrowserContext
import pathlib
import json

anvanum = "edhovhannisyan97@gmail.com"
gaxtnabar = "Eh160899insta!"
username = "eddie.thingz"


def check_follower(page: Page, path: str):
    page.goto(f"https://www.instagram.com{path}")

    following_link_locator = page.locator("[role='link']")
    btn = following_link_locator.filter(has_text="following")
    btn.click()

    time.sleep(2)

    accounts_locator = page.locator("[role='dialog'] [role='link']")
    my_account_link = accounts_locator.filter(has_text=username)

    print(f"Debug: current acc name in following list: {my_account_link.count()}")

    if my_account_link.count() == 0:
        print(f"Not following alert: {path} -> {username}")


def store_cookies(page: Page):
    cookies = page.context.cookies()

    session_path = "sessions/latest.json"
    serialized_data = json.dumps(cookies)
    pathlib.Path(session_path).write_text(serialized_data)

    print("Stored latest cookies in session!")

    if page:
        page.close()


def restore_cookies(context: BrowserContext):
    restored = False
    session_path = "sessions/latest.json"

    if os.path.exists(session_path):
        cookie_data = json.loads(pathlib.Path(session_path).read_text())
        context.add_cookies(cookie_data)

        print("Cookies added!")
        restored = True

    return restored


def manual_login(page: Page, persist_session=True):
    btn = page.get_by_text("Allow all cookies")
    btn.click()

    btn = page.get_by_role("dialog").get_by_text("Log in")
    btn.click()

    # Fill credentials
    username_input = page.get_by_label("Phone number, username, or email")
    username_input.fill(anvanum)

    pwd_input = page.get_by_label("Password")
    pwd_input.fill(gaxtnabar)

    # Hit the submit button to log in.
    submit_btn = page.locator("css=#loginForm [type=submit]")
    submit_btn.click()

    if persist_session:
        store_cookies(page)


def run(playwright: Playwright):
    browser = playwright.chromium.launch(headless=False, slow_mo=300)
    context = browser.new_context()
    page = context.new_page()

    restored = restore_cookies(context)

    # Log in manually if session did not exist before
    # @Todo: check if session was expired
    if not restored:
        manual_login(page)

    page.goto("https://www.instagram.com")

    # Go to Profile page
    link_lokator = page.locator("[role='link']")
    profile_link = link_lokator.filter(has_text="Profile")
    profile_link.click()

    # Open popup of people user follows
    following_link = link_lokator.filter(has_text="following")
    following_link.click()

    time.sleep(3)

    following_links_locator = page.locator("css=div[role=dialog] a[role=link]")
    following_links = following_links_locator.all()

    print("Found links", len(following_links))

    for index, link in enumerate(following_links):
        name = link.text_content()
        nickname_with_path = link.get_attribute("href")

        p2 = context.new_page()
        check_follower(p2, nickname_with_path)
        p2.close()

        print(f"User: {name}, URL: {nickname_with_path}")

    print("Page title", page.title())

    time.sleep(50)
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
