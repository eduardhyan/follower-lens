from pathlib import Path
import json


class FileCache:
    def __init__(self, file_path: str, preload: bool = True):
        if not file_path.endswith("json"):
            file_path = f"{file_path}.json"

        self.file = Path(file_path)
        self.buffer = {}

        if preload:
            self.load_cache()

    def __len__(self):
        return len(self.buffer)

    def __iter__(self):
        return iter(self.buffer)

    def set(self, key, value):
        self.buffer[key] = value

    def get(self, key):
        return self.buffer.get(key, None)

    def setIfAbsent(self, key, value=None):
        if not self.hasKey(key):
            self.set(key, value)
            return True

        return False

    def hasKey(self, key):
        return key in self.buffer

    def save(self):
        self.ensure_file()
        self.file.write_text(self.serialize())

    def serialize(self):
        return json.dumps(self.buffer)

    def load_cache(self):
        self.ensure_file()

        try:
            self.buffer = json.loads(self.file.read_text())
        except json.decoder.JSONDecodeError:
            self.buffer = {}

    def ensure_file(self):
        if not self.file.exists():
            self.file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.file.as_posix(), "w", encoding="utf-8") as f:
                f.close()
