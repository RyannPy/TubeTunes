import subprocess
from yt_dlp import YoutubeDL


def get_audio_stream(video_url):
    ydl_opts = {
        "format": "bestaudio",
        "quiet": True
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=False)

    return info["url"]


def play_audio(audio_url):
    subprocess.run(
        ["mpv", audio_url]
    )