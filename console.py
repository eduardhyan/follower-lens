"""
This module provides functions for printing messages and tables
to the console using the rich library.
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

import constants

console = Console()


def print_rate_limit_error():
    """
    Prints a rate limit error message to the console.
    """
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


def print_followers_stats(insights, include_haters=True, include_ghosts=True):
    """
    Prints a table of follower statistics to the console.

    Args:
        insights (dict): A dictionary containing follower insights.
        include_haters (bool): Whether to include haters in the table.
        include_ghosts (bool): Whether to include ghosts in the table.
    """
    table = Table(title="Instagram Followers")
    table.add_column("#", justify="center", style="cyan", no_wrap=True)
    table.add_column("Username", justify="left", style="cyan", no_wrap=True)

    if include_haters:
        table.add_column("Following me back?", justify="left", style="magenta")

    if include_ghosts:
        table.add_column("I follow them?", justify="left", style="magenta")

    table.add_column("Account URL", justify="left", style="cyan")

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
            f"{constants.IG_BASE_URL}/{key}/",
        ]

        if not include_haters:
            del row_data[2]

        if not include_ghosts:
            del row_data[3]

        table.add_row(*row_data)
        idx += 1

    console.print(table)
