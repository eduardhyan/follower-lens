import sys
import time
from enum import Enum
from pathlib import Path

import inquirer
from inquirer.themes import BlueComposure
from playwright.sync_api import Playwright, sync_playwright

import auth
import cli
import commands
import config
import console
import constants
from analyzer import FollowerInsights
from cache import FollowerCache

follower_insights = FollowerInsights()


def run_simplified(playwright: Playwright, repo: FollowerCache):
    browser = playwright.chromium.launch(headless=False, slow_mo=300)
    context = browser.new_context()
    page = context.new_page()

    # 1. Restore cookies to not log in again
    restored = auth.restore_cookies(context)
    print(f"Session restored: {restored}")

    page.goto(f"{constants.IG_BASE_URL}/")

    # 2. Check if Instagram blocks the bot
    if page.locator(":has-text('Something went wrong')").count():
        console.print_rate_limit_error()
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
    commands.profile.extract_followers(page=page, repo=repo, my_followers=True)

    # 8. Close the dialog
    page.locator('[role=dialog] svg:has-text("Close")').click()

    # 9. Get all followings
    commands.profile.extract_followers(page=page, repo=repo, my_followers=False)

    # 10. Shut down the browser
    browser.close()

    print("✅ Successfully collected all information about your followers!")


def clear_cache():
    Path(f"cache/{config.Account.get_encoded_username()}.json").write_text("")
    print(
        "Cache cleared, the previously stored information about your followers is removed.\n"
    )


def main():
    cli.print_introduction()
    cli.get_credentials()

    repo = FollowerCache(f"cache/{config.Account.get_encoded_username()}", preload=True)
    follower_insights.load(repo.followers.to_list(), repo.followings.to_list())

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
        answers = inquirer.prompt(questions, theme=BlueComposure())
        action = answers["command"]

        match action:
            case Command.START:
                with sync_playwright() as playwright:
                    run_simplified(playwright, repo)

                    follower_insights.load(
                        repo.followers.to_list(), repo.followings.to_list()
                    )

            case Command.LIST_ALL:
                console.print_followers_stats(
                    insights=follower_insights.get_full_insights()
                )

            case Command.LIST_HATERS:
                console.print_followers_stats(
                    insights=follower_insights.get_full_insights(),
                    include_ghosts=False,
                )

            case Command.LIST_GHOSTS:
                console.print_followers_stats(
                    insights=follower_insights.get_full_insights(),
                    include_haters=False,
                )

            case Command.CLEAR_CACHE:
                clear_cache()
                follower_insights.flush()

            case Command.EXIST:
                print("Shutting down, see you next time 👋 ...")
                running = False
            case _:
                print(f"Command {action} is not available yet!")


if __name__ == "__main__":
    main()
