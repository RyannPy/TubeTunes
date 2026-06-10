from playlist import get_playlist
from queue_manager import QueueManager
from player import Player

from cli import parse_args

# parse input
args = parse_args()
# get url dan playlist
playlist_url = args.playlist_url
playlist = get_playlist(playlist_url)

# manage queue
queue = QueueManager(
    playlist["entries"],
    shuffle=args.shuffle

)

player = Player()

# play songs
while queue.has_next():

    try:

        # TITLE
        print(f"▶ {queue.current_title()}")

        # COMING UP
        print("\nNext Up:")
        for i, song in enumerate(
            queue.upcoming(),
            start=1
        ):
            print(
                f"{i}. {song['title']}"
            )

        # PLAY
        player.play(queue.current_url())

    except Exception as e:

        print(e)

    queue.advance()