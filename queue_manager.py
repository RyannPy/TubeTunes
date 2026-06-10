class QueueManager:

    def __init__(self, songs):
        self.songs = songs
        self.index = 0

    def has_next(self):
        return self.index < len(self.songs)
    
    def current(self):
        if 0 <= self.index < len(self.songs):
            return self.songs[self.index]
        return None
    
    def advance(self):
        self.index += 1