"""
This module provides the FollowerInsights class for analyzing follower and following data.

Classes:
    FollowerInsights: A class for analyzing Instagram followers and followings.
"""


class FollowerInsights:
    """
    A class for analyzing Instagram followers and followings.
    """

    def __init__(self):
        self.followers = set()
        self.followings = set()

    def load(self, new_followers_list: list[str], new_followings_list: list[str]):
        """
        Loads new follower and following data.

        Args:
            new_followers_list (list[str]): A list of new followers.
            new_followings_list (list[str]): A list of new followings.
        """
        self.followers = set(new_followers_list)
        self.followings = set(new_followings_list)

    def get_all_followers(self) -> list[str]:
        """
        Returns a list of all followers.

        Returns:
            list[str]: A list of all followers.
        """
        return list(self.followers)

    def get_haters_list(self) -> list[str]:
        """
        Returns a list of users who don't follow back.

        Returns:
            list[str]: A list of users who don't follow back.
        """
        return list(self.followings - self.followers)

    def get_ghosts_list(self) -> list[str]:
        """
        Returns a list of users who follow but are not followed back.

        Returns:
            list[str]: A list of users who follow but are not followed back.
        """
        return list(self.followers - self.followings)

    def get_full_insights(self) -> dict[str, dict[str, bool]]:
        """
        Returns a dictionary with full insights on followers and followings.

        Returns:
            dict[str, dict[str, bool]]: A dictionary with full insights.
        """
        insights = {}

        for name in self.followers:
            if name not in insights:
                insights[name] = self._create_empty_stat_record()

            # They are in my followers list but not in my followings = I don't follow them
            insights[name]["is_ghost"] = name not in self.followings

        for name in self.followings:
            if name not in insights:
                insights[name] = self._create_empty_stat_record()

            # They are not in my followers list = they don't follow me
            insights[name]["is_hater"] = name not in self.followers

        return insights

    def flush(self):
        """
        Empties internal lists of followers and followings
        """
        self.followers = set()
        self.followings = set()

    def _create_empty_stat_record(self) -> dict[str, bool]:
        """
        Creates an empty statistics record.

        Returns:
            dict[str, bool]: An empty statistics record.
        """
        return {
            "is_hater": False,  # I follow, they don't
            "is_ghost": False,  # They follow, I don't
        }
