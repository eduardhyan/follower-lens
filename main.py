import hashlib
import json
import time

from playwright.sync_api import Page, Playwright, sync_playwright

import auth
import cli
import commands
import config
from cache import FileCache

BASE_URL = "https://www.instagram.com"


def check_follower(page: Page, path: str):
    page.goto(f"{BASE_URL}{path}")

    following_link_locator = page.locator("[role='link']")
    btn = following_link_locator.filter(has_text="following")
    btn.click()

    time.sleep(2)

    accounts_locator = page.locator("[role='dialog'] [role='link']")
    my_account_link = accounts_locator.filter(has_text=config.Account.username)

    if my_account_link.count() == 0:
        print(f"Not following alert: {path} -> {config.Account.username}")
        return False

    return True


def run(playwright: Playwright):
    cache = FileCache(f"cache/{config.Account.get_encoded_username()}", preload=True)

    browser = playwright.chromium.launch(headless=False, slow_mo=300)
    context = browser.new_context()
    page = context.new_page()

    restored = auth.restore_cookies(context)
    print(f"Session restored: {restored}")

    page.goto(f"{BASE_URL}/")

    # Log in manually if session did not exist before or
    # user got redirected to homepage (possibliy expired session)
    if not restored or not commands.is_homepage(page):
        print("Logging in manually. Session restoration failed!")
        auth.manual_login(page)

    # Go to Profile page
    link_lokator = page.locator("[role='link']")
    profile_link = link_lokator.filter(has_text="Profile")
    profile_link.click()

    # Open popup of people user follows
    following_link = link_lokator.filter(has_text="following")
    following_link.click()

    follower_usernames = []
    # Extract first five names of followers
    for _ in range(5):
        time.sleep(2)

        following_links_locator = page.locator("css=div[role=dialog] a[role=link] span")
        following_links = following_links_locator.all()

        current_chunk = []
        for link in following_links:
            name = link.text_content()
            print("Name", name)
            current_chunk.append(name)

        follower_usernames = list(set(follower_usernames + current_chunk))

        with open("followers.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(follower_usernames))

        # Scroll followers list to its' bottom
        page.evaluate("""() => {
            const list = document.querySelector('[role=dialog] [style*="overflow: hidden auto;"]').parentElement
            list.scrollTo({top: list.scrollHeight, behavior: "smooth"})
        }""")

    for _, name in enumerate(follower_usernames):
        nickname_with_path = f"/{name}/"

        print("-" * 40)
        print(f"User: {name or nickname_with_path}, URL: {nickname_with_path}")

        following_data = cache.get(nickname_with_path)
        print("Following data", following_data)
        if isinstance(following_data, bool):
            print(
                f"Skipping {nickname_with_path}, detected in cache that this account "
                f"follows you: {following_data}"
            )
            continue

        p2 = context.new_page()
        is_following = check_follower(p2, nickname_with_path)

        cache.set(nickname_with_path, is_following)
        cache.save()

        p2.close()

    browser.close()


def main():
    cli.get_credentials()

    with sync_playwright() as playwright:
        run(playwright)


if __name__ == "__main__":
    main()
