import math
import re
import time

from playwright.sync_api import Page

from cache import FileCache


def extract_followers(page: Page, cache: FileCache, my_followers=True):
    # Open popup of people user follows
    btn_text = "followers" if my_followers else "following"
    following_link = page.locator(f"header ul [role=link]:has-text('{btn_text}')")

    followers_count = "".join(re.findall(r"\d+", following_link.text_content()))
    followers_count = int(followers_count) if followers_count else 0

    extraction_page_size = 12
    max_expected_cycles = math.ceil(followers_count / extraction_page_size)
    print(
        f"Detected {followers_count} {btn_text}. Will do max {max_expected_cycles} cycles"
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

        for link in following_links:
            name = link.text_content()
            cache.set(name)

        # persist names in cache
        cache.save()

        # Scroll followers list to its' bottom
        page.evaluate("""() => {
            const list = document.querySelector('[role=dialog] [style*="overflow: hidden auto;"]').parentElement
            list.scrollTo({top: list.scrollHeight, behavior: "smooth"})
        }""")
