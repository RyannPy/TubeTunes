from playlist import get_playlist
from player import get_audio_stream, play_audio

playlist_url = input("Enter the Playlist URL: ")

playlist = get_playlist(playlist_url)
total = len(playlist["entries"])


for i, video in enumerate(playlist["entries"], start=1):

    try:
        title = video["title"]

        print(
            f"\n[{i}/{total}] {title}"
        )

        video_url = (
            f"https://www.youtube.com/watch?v={video['id']}"
        )

        print(f"\n▶ Now Playing: {title}")

        audio_url = get_audio_stream(video_url)

        play_audio(audio_url)

    except Exception as e:
        print(f"Skipped: {title}")
        print(e)