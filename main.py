from playlist import get_playlist
from player import get_audio_stream



url = input("Enter the playlist URL: ")
playlist = get_playlist(url)

first_video = next(iter(playlist['entries']))
video_url = f"https://www.youtube.com/watch?v={first_video['id']}"


stream_url = get_audio_stream(video_url)

print(f"Audio stream URL: {stream_url}")

for video in playlist['entries']:
    print(video['title'])