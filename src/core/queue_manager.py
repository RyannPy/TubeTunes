import random


class QueueManager:

    def __init__(self, songs: list, shuffle: bool = False):
        self.songs = songs.copy()

        if shuffle:
            random.shuffle(self.songs)

        self.index = 0

    def has_next(self) -> bool:
        return self.index < len(self.songs)

    def current(self) -> dict:
        return self.songs[self.index]

    def advance(self) -> None:
        self.index += 1

    def current_url(self) -> str:
        current = self.current()
        return f"https://youtube.com/watch?v={current['id']}"

    def current_title(self) -> str:
        current = self.current()
        return current["title"]

    def upcoming(self, limit: int = 3) -> list:
        return self.songs[self.index + 1 : self.index + 1 + limit]
