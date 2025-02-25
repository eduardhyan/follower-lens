"""
This module provides classes for managing a cache of followers and followings
using JSON files. It includes a SetBuffer class for storing unique items in a set
and a FollowerCache class for handling the serialization and deserialization of
follower data to and from a JSON file.

Classes:
    SetBuffer: A buffer that stores unique items in a set.
    FollowerCache: A cache that stores followers and followings in a JSON file.

Usage example:
    cache = FollowerCache("path/to/cache_file")
    cache.followers.add("follower1")
    cache.followings.add("following1")
    cache.save()
    cache.load_cache()
"""

import json
from pathlib import Path


class SetBuffer:
    """A buffer that stores unique items in a set."""

    def __init__(self):
        self.storage = set()

    def __len__(self):
        return len(self.storage)

    def __iter__(self):
        return iter(self.storage)

    def add(self, value):
        """Add a value to the buffer."""
        self.storage.add(value)

    def contains(self, key):
        """Check if a key is in the buffer."""
        return key in self.storage

    def to_list(self):
        """Get the buffer contents as a list."""
        return list(self.storage)


class FollowerCache:
    """A cache that stores followers and followings in a JSON file."""

    def __init__(self, file_path: str, preload: bool = True):
        if not file_path.endswith(".json"):
            file_path = f"{file_path}.json"

        self.file = Path(file_path)
        self.followers = SetBuffer()
        self.followings = SetBuffer()

        if preload:
            self.load_cache()

    def save(self):
        """Save the current state to the file."""
        self.ensure_file_exists()
        self.file.write_text(self.serialize())

    def serialize(self):
        """Serialize the buffer contents to a JSON string."""
        return json.dumps(
            {
                "followers": self.followers.to_list(),
                "followings": self.followings.to_list(),
            }
        )

    def load_cache(self):
        """Load the cache from the file."""
        self.ensure_file_exists()

        try:
            contents = json.loads(self.file.read_text())

            if "followers" not in contents or "followings" not in contents:
                raise json.decoder.JSONDecodeError(
                    doc=self.file, msg="Cache contents are corrupted", pos=0
                )

            self.followers = SetBuffer()
            self.followings = SetBuffer()

            for follower in contents.get("followers", []):
                self.followers.add(follower)

            for following in contents.get("followings", []):
                self.followings.add(following)

        except json.decoder.JSONDecodeError:
            self.followers = SetBuffer()
            self.followings = SetBuffer()

    def ensure_file_exists(self):
        """Ensure the cache file exists, creating it if necessary."""
        if not self.file.exists():
            self.file.parent.mkdir(parents=True, exist_ok=True)
            self.file.touch()
