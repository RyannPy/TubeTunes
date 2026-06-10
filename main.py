from playlist import get_playlist
from queue_manager import QueueManager
from player import get_audio_stream
from player import play_audio

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
# play songs
while queue.has_next():

    video = queue.current()

    try:

        title = video["title"]

        video_url = (
            f"https://youtube.com/watch?v={video['id']}"
        )

        print(f"▶ {title}")

        audio_url = get_audio_stream(
            video_url
        )

        play_audio(audio_url)

    except Exception as e:

        print(e)

    queue.advance()