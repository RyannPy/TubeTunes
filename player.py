from yt_dlp import YoutubeDL
import subprocess


class Player:

    def get_audio_stream(self, video_url):

        ydl_opts = {
            "format": "bestaudio",
            "quiet": True
        }

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(
                video_url,
                download=False
            )

        return info["url"]

    def play(self, video_url):

        audio_url = self.get_audio_stream(
            video_url
        )

        subprocess.run(
            ["mpv", audio_url]
        )