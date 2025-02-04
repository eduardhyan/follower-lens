from playwright.sync_api import Page


def is_homepage(page: Page):
    return page.get_by_label("For you") is not None
