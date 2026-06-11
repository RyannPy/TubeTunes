import subprocess
from yt_dlp import YoutubeDL


class PlaybackError(Exception):
    """Raised when audio stream extraction or mpv playback fails."""
    pass


class Player:

    def get_audio_stream(self, video_url: str) -> str:
        """Resolve the best audio stream URL for a YouTube video.

        Raises PlaybackError if yt-dlp cannot extract the stream.
        """
        ydl_opts = {
            "format": "bestaudio",
            "quiet": True,
        }

        try:
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
        except Exception as e:
            raise PlaybackError(
                f"Could not extract audio stream: {e}"
            ) from e

        return info["url"]

    def play(self, video_url: str) -> None:
        """Resolve audio stream and play it via mpv.

        Raises PlaybackError if mpv is not installed or playback fails.
        """
        audio_url = self.get_audio_stream(video_url)

        try:
            subprocess.run(["mpv", audio_url], check=False)
        except FileNotFoundError:
            raise PlaybackError(
                "mpv is not installed. Please install mpv to play audio."
            )
        except Exception as e:
            raise PlaybackError(f"Playback failed: {e}") from e
