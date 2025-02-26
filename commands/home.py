"""
This module provides functions to interact with the Instagram homepage.
"""

from playwright.sync_api import Page


def is_homepage(page: Page) -> bool:
    """
    Check if the current page is the Instagram homepage.

    Args:
        page (Page): The Playwright page object.

    Returns:
        bool: True if the current page is the Instagram homepage, False otherwise.
    """
    return page.get_by_label("For you") is not None
