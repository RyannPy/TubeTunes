import random


class QueueManager:

    def __init__(
        self,
        songs,
        shuffle=False
    ):

        self.songs = songs.copy()

        if shuffle:
            random.shuffle(self.songs)

        self.index = 0

    def has_next(self):
        return self.index < len(self.songs)

    def current(self):
        return self.songs[self.index]

    def advance(self):
        self.index += 1

    def current_url(self):

        current = self.current()

        return (
            f"https://youtube.com/watch?v="
            f"{current['id']}"
        )
    
    def current_title(self):
        current = self.current()

        return current["title"]
    
    def upcoming(self, limit=3):

        return self.songs[
            self.index + 1 :
            self.index + 1 + limit
        ]