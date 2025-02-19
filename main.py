import json
import math
import re
import sys
import time
from enum import Enum
from pathlib import Path

import inquirer
from inquirer.themes import BlueComposure
from playwright.sync_api import Page, Playwright, sync_playwright
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

import auth
import cli
import commands
import config
from cache import FileCache

BASE_URL = "https://www.instagram.com"

console = Console()


def check_follower(page: Page, path: str):
    page.goto(f"{BASE_URL}{path}")

    following_link_locator = page.locator("[role='link']")
    btn = following_link_locator.filter(has_text="following")

    if btn.count() == 0:
        print(f"Zero following: {path} -> {config.Account.username}")
        return False

    # Open following modal
    btn.click()

    # We need to wait for the followers list to be fetched
    # here we'll wait for at least one profile picture to be shown
    page.wait_for_selector(
        'css=[role="dialog"] img[alt$="profile picture"]'
    ).is_visible()

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

    followers_count = "".join(re.findall(r"\d+", following_link.text_content()))
    followers_count = int(followers_count) if followers_count else 0

    extraction_page_size = 12
    max_expected_cycles = math.ceil(followers_count / extraction_page_size)
    print(
        f"Detected {followers_count} followers. Will do max {max_expected_cycles} cycles"
    )

    following_link.click()

    prev_last_user = None
    # Extract first five names of followers
    for _ in range(max_expected_cycles):
        time.sleep(2)

        # In cache we have exactly same number of followers
        # as user has at this moment, no need to fetch follower names again
        if followers_count == len(cache):
            break

        following_links_locator = page.locator("css=div[role=dialog] a[role=link] span")
        following_links = following_links_locator.all()

        # If after fetching new set of followers and the
        # modal's content doesn't change, then no more followers left to analyze
        new_last_user = following_links[-1].text_content()
        if new_last_user == prev_last_user:
            break
        else:
            prev_last_user = new_last_user

        current_chunk = []
        for link in following_links:
            name = link.text_content()

            if cache.setIfAbsent(name):
                # If the value previously didnt exist in cache
                # add it to the follower_usernames to later check status of following
                current_chunk.append(name)
            else:
                print(f"Data for {name} already exists in cache, will skip...")

        # persist names in cache
        cache.save()

        # Scroll followers list to its' bottom
        page.evaluate("""() => {
            const list = document.querySelector('[role=dialog] [style*="overflow: hidden auto;"]').parentElement
            list.scrollTo({top: list.scrollHeight, behavior: "smooth"})
        }""")

    for name in cache:
        nickname_with_path = f"/{name}/"

        print("-" * 40)
        print(f"User: {name or nickname_with_path}, URL: {nickname_with_path}")

        following_data = cache.get(name)
        print("Following data", following_data)
        if isinstance(following_data, bool):
            print(
                f"Skipping {name}, following status detected. Follows you: {following_data} "
            )
            continue

        p2 = context.new_page()
        is_following = check_follower(p2, nickname_with_path)

        cache.set(name, is_following)
        cache.save()

        p2.close()

    browser.close()


def run_simplified(playwright: Playwright):
    cache_followers = FileCache(
        f"cache/{config.Account.get_encoded_username()}.followers", preload=True
    )
    cache_followings = FileCache(
        f"cache/{config.Account.get_encoded_username()}.followings", preload=True
    )

    browser = playwright.chromium.launch(headless=False, slow_mo=300)
    context = browser.new_context()
    page = context.new_page()

    # 1. Restore cookies to not log in again
    restored = auth.restore_cookies(context)
    print(f"Session restored: {restored}")

    # 2. Open user profile
    # page.goto(f"{BASE_URL}/{config.Account.username}")
    page.goto(f"{BASE_URL}/")

    # 3. Check if Instagram blocks the bot
    if page.locator(":has-text('Something went wrong')").count():
        message = (
            "[bold yellow]Instagram Rate Limit Reached! 🚧[/bold yellow]\n\n"
            "Instagram has temporarily restricted actions to prevent spam-like behavior.\n"
            "⏳ Please wait a few minutes before trying again.\n"
        )

        console.print(
            Panel.fit(
                message, title="[cyan]Action Temporarily Blocked[/cyan]", style="yellow"
            )
        )
        sys.exit(0)

    # 4. If cookie form appeared, close it
    btn = page.get_by_text("Allow all cookies")
    if btn.count():
        btn.click()
        time.sleep(2)

    # 5. Account is private, we should submit login form
    if not restored and not config.Account.is_public:
        # 5.1.1 Open log in form if appeared
        btn = page.locator('[role=dialog] [role=button]:has-text("Log in")')
        if btn.count():
            btn.click()

        # 5.1.2 Fill the login form
        auth.manual_login(page)

        # 5.1.3 Go to Profile page
        link_lokator = page.locator("[role='link']")
        profile_link = link_lokator.filter(has_text="Profile")
        profile_link.click()

    elif restored and not config.Account.is_public:
        # 5.2.1 Go to Profile page
        link_lokator = page.locator("[role='link']")
        profile_link = link_lokator.filter(has_text="Profile")
        profile_link.click()

        page.wait_for_url(f"**/{config.Account.username}/**")

    elif config.Account.is_public:
        # Store cookies after closing modals/popups
        auth.store_cookies(page)

    time.sleep(2)

    # 6. Get all followers
    commands.profile.extract_followers(
        page=page, cache=cache_followers, my_followers=True
    )

    # 7. Close the dialog
    page.locator('[role=dialog] svg:has-text("Close")').click()

    # 8. Get all followings
    commands.profile.extract_followers(
        page=page, cache=cache_followings, my_followers=False
    )

    # 9. Shut down the browser
    browser.close()

    # 10. Print all findings
    haters = []
    for key in cache_followings:
        if key not in cache_followers:
            haters.append(key)

    table = Table(title="Instagram Followers")
    table.add_column("#", justify="center", style="cyan", no_wrap=True)
    table.add_column("Username", justify="left", style="cyan", no_wrap=True)
    table.add_column("Following me back?", justify="left", style="magenta")
    table.add_column("Account URL", justify="left", style="cyan")

    idx = 1
    for username in haters:
        label_follows_back = "[red]No[/red]"

        table.add_row(
            str(idx),
            username,
            label_follows_back,
            f"{BASE_URL}/{username}/",
        )
        idx += 1

    console.print(table)


def display_followers(only_haters=False):
    try:
        follower_stats = json.loads(
            Path(f"cache/{config.Account.get_encoded_username()}.json").read_text()
        )
    except:
        follower_stats = []

    table = Table(title="Instagram Followers")
    table.add_column("#", justify="center", style="cyan", no_wrap=True)
    table.add_column("Username", justify="left", style="cyan", no_wrap=True)
    table.add_column("Following me back?", justify="left", style="magenta")
    table.add_column("Account URL", justify="left", style="cyan")

    idx = 1
    for key in follower_stats:
        label_follows_back = "[red]No[/red]"

        if follower_stats[key]:
            label_follows_back = "[green]Yes[/green]"

            # If the user is following back (value is true)
            # we don't show them in the table
            if only_haters:
                continue

        table.add_row(
            str(idx),
            key,
            label_follows_back,
            f"{BASE_URL}/{key}/",
        )
        idx += 1

    console.print(table)


def clear_cache():
    Path(f"cache/{config.Account.get_encoded_username()}.json").write_text("")
    print(
        "Cache cleared, the previously stored information about your followers is removed.\n"
    )


def main():
    cli.print_introduction()
    cli.get_credentials()

    Command = Enum(
        "Command",
        [
            ("START", 1),
            ("LIST_HATERS", 2),
            ("LIST_ALL", 3),
            ("CLEAR_CACHE", 4),
            ("EXIST", 5),
        ],
    )

    questions = [
        inquirer.List(
            "command",
            message="🔍 Choose one of the actions below",
            choices=[
                (
                    "Find Unfollowers – (Start finding people who don't follow me back)",
                    Command.START,
                ),
                (
                    "Preview Unfollowers – (Preview only people who don’t follow me back)",
                    Command.LIST_HATERS,
                ),
                (
                    "View Full Follower List – (Preview full list of followers/non-followers)",
                    Command.LIST_ALL,
                ),
                (
                    "Clear the cache – (Delete locally stored data from previous executions)",
                    Command.CLEAR_CACHE,
                ),
                ("Cancel & Exit – (Close the application and Exit)", Command.EXIST),
            ],
        )
    ]

    running = True
    while running:
        print("\n" + "=" * 40)
        print("General Menu")
        print("=" * 40 + "\n")

        answers = inquirer.prompt(questions, theme=BlueComposure())
        action = answers["command"]

        match action:
            case Command.START:
                with sync_playwright() as playwright:
                    run_simplified(playwright)

            case Command.LIST_ALL:
                display_followers()

            case Command.LIST_HATERS:
                display_followers(only_haters=True)

            case Command.CLEAR_CACHE:
                clear_cache()

            case Command.EXIST:
                print("Shutting down, see you next time 👋 ...")
                running = False
            case _:
                print(f"Command {action} is not available yet!")


if __name__ == "__main__":
    main()
