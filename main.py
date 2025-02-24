import json
import sys
import time
from enum import Enum
from pathlib import Path

import inquirer
from inquirer.themes import BlueComposure
from playwright.sync_api import Playwright, sync_playwright
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

import auth
import cli
import commands
import config
from cache import FileCache
from analyzer import FollowerInsignts

BASE_URL = "https://www.instagram.com"

console = Console()

follower_insights = FollowerInsignts()


def run_simplified(playwright: Playwright):
    cache_followers = FileCache(
        f"cache/{config.Account.get_encoded_username()}.followers", preload=True
    )
    cache_followings = FileCache(
        f"cache/{config.Account.get_encoded_username()}.followings", preload=True
    )

    follower_insights.load(
        cache_followers.get_as_list(), cache_followings.get_as_list()
    )

    browser = playwright.chromium.launch(headless=False, slow_mo=300)
    context = browser.new_context()
    page = context.new_page()

    # 1. Restore cookies to not log in again
    restored = auth.restore_cookies(context)
    print(f"Session restored: {restored}")

    page.goto(f"{BASE_URL}/")

    # 2. Check if Instagram blocks the bot
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

    # 3. Fill the login form
    if restored:
        # 6. Go to Profile page
        link_lokator = page.locator("[role='link']")
        profile_link = link_lokator.filter(has_text="Profile")
        profile_link.click()

        page.wait_for_url(f"**/{config.Account.username}/**")
        time.sleep(2)
    else:
        auth.manual_login(page)

    # 7. Get all followers
    commands.profile.extract_followers(
        page=page, cache=cache_followers, my_followers=True
    )

    # 8. Close the dialog
    page.locator('[role=dialog] svg:has-text("Close")').click()

    # 9. Get all followings
    commands.profile.extract_followers(
        page=page, cache=cache_followings, my_followers=False
    )

    # 10. Shut down the browser
    browser.close()

    # 11. Print all findings
    haters = []
    for key in cache_followings:
        if key not in cache_followers:
            haters.append(key)

    print_followers_pretty(haters)


def print_followers_pretty(haters):
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


def display_followers_stats(include_haters=True, include_ghosts=True):
    table = Table(title="Instagram Followers")
    table.add_column("#", justify="center", style="cyan", no_wrap=True)
    table.add_column("Username", justify="left", style="cyan", no_wrap=True)

    if include_haters:
        table.add_column("Following me back?", justify="left", style="magenta")

    if include_ghosts:
        table.add_column("I follow them?", justify="left", style="magenta")

    table.add_column("Account URL", justify="left", style="cyan")

    insights = follower_insights.get_full_insights()
    idx = 1
    for key, record in insights.items():
        is_ghost, is_hater, is_friend = (
            record["is_ghost"],
            record["is_hater"],
            not record["is_hater"] and not record["is_ghost"],
        )

        label_follows_back = (
            "[green]Yes[/green]" if not is_hater else "[red]No 😾[/red]"
        )
        label_I_follow_them = (
            "[green]Yes[/green]" if not is_ghost else "[red]No 👻[/red]"
        )

        if is_friend and (include_ghosts ^ include_haters):
            continue

        if not include_ghosts and is_ghost:
            continue

        if not include_haters and is_hater:
            continue

        row_data = [
            str(idx),
            key,
            label_follows_back,
            label_I_follow_them,
            f"{BASE_URL}/{key}/",
        ]

        if not include_haters:
            del row_data[2]

        if not include_ghosts:
            del row_data[3]

        table.add_row(*row_data)
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

    cache_followers = FileCache(
        f"cache/{config.Account.get_encoded_username()}.followers", preload=True
    )
    cache_followings = FileCache(
        f"cache/{config.Account.get_encoded_username()}.followings", preload=True
    )

    follower_insights.load(
        cache_followers.get_as_list(), cache_followings.get_as_list()
    )

    Command = Enum(
        "Command",
        [
            ("START", 1),
            ("LIST_HATERS", 2),
            ("LIST_GHOSTS", 3),
            ("LIST_ALL", 4),
            ("CLEAR_CACHE", 5),
            ("EXIST", 6),
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
                    "Preview Ghosts – (Preview only people who follow me but I don't folllow them)",
                    Command.LIST_GHOSTS,
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
                display_followers_stats()

            case Command.LIST_HATERS:
                display_followers_stats(include_ghosts=False)

            case Command.LIST_GHOSTS:
                display_followers_stats(include_haters=False)

            case Command.CLEAR_CACHE:
                clear_cache()

            case Command.EXIST:
                print("Shutting down, see you next time 👋 ...")
                running = False
            case _:
                print(f"Command {action} is not available yet!")


if __name__ == "__main__":
    main()
