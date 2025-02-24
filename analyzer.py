class FollowerInsignts:
    followers: set[str]
    followings: set[str]

    def load(self, new_followers_list: list[str], new_followings_list: list[str]):
        self.followers = set(new_followers_list)
        self.followings = set(new_followings_list)

    def get_all_followers(self):
        return list(self.followers)

    def get_haters_list(self):
        return list(self.followings - self.followers)

    def get_ghosts_list(self):
        return list(self.followers - self.followings)

    def get_full_insights(self):
        out = {}

        for name in self.followers:
            if name not in out:
                out[name] = self.create_empty_stat_record()

            # They are in my followers list but not in my followings = I don't follow them
            out[name]["is_ghost"] = name not in self.followings

        for name in self.followings:
            if name not in out:
                out[name] = self.create_empty_stat_record()

            # They are not in my followers list = they don't follow me
            out[name]["is_hater"] = name not in self.followers

        return out

    def create_empty_stat_record(self):
        return {
            "is_hater": None,  # I follow, they don't
            "is_ghost": None,  # They follow, I don't
        }
