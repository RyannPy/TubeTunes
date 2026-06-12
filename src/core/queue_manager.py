import random


class QueueManager:

    def __init__(self, songs: list, shuffle: bool = False):
        self.songs = songs.copy()

        if shuffle:
            random.shuffle(self.songs)

        self.index = 0

    # ------------------------------------------------------------------
    # Forward navigation
    # ------------------------------------------------------------------

    def has_next(self) -> bool:
        return self.index < len(self.songs)

    def current(self) -> dict:
        return self.songs[self.index]

    def advance(self) -> None:
        self.index += 1

    # ------------------------------------------------------------------
    # Backward navigation  (V3.0 addition)
    # ------------------------------------------------------------------

    def has_previous(self) -> bool:
        """Return True if there is a song before the current index."""
        return self.index > 0

    def back(self) -> None:
        """Move the index one step backward.

        Callers should check has_previous() first.
        Does nothing (clamps at 0) if already at the first song.
        """
        if self.index > 0:
            self.index -= 1

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def current_url(self) -> str:
        current = self.current()
        return f"https://youtube.com/watch?v={current['id']}"

    def current_title(self) -> str:
        current = self.current()
        return current["title"]

    def upcoming(self, limit: int = 3) -> list:
        return self.songs[self.index + 1 : self.index + 1 + limit]
