import subprocess
from yt_dlp import YoutubeDL


class PlaybackError(Exception):
    """Raised when audio stream extraction or mpv playback fails."""
    pass


class Player:
    """Wraps mpv as a controllable subprocess.

    V3.0: uses Popen so the process can be stopped externally.
    V3.1 extension point: replace Popen with mpv IPC socket for pause/seek/volume.
    """

    def __init__(self):
        self._process: subprocess.Popen | None = None

    # ------------------------------------------------------------------
    # Stream resolution
    # ------------------------------------------------------------------

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

    # ------------------------------------------------------------------
    # Process control
    # ------------------------------------------------------------------

    def play(self, video_url: str) -> None:
        """Resolve audio stream and launch mpv via Popen (non-blocking).

        Stores the process reference in self._process so it can be
        stopped via stop() while music is playing.

        Raises PlaybackError if mpv is not installed or cannot start.
        """
        audio_url = self.get_audio_stream(video_url)

        try:
            self._process = subprocess.Popen(
                ["mpv", "--no-terminal", audio_url],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except FileNotFoundError:
            raise PlaybackError(
                "mpv is not installed. Please install mpv to play audio."
            )
        except Exception as e:
            raise PlaybackError(f"Could not start mpv: {e}") from e

    def stop(self) -> None:
        """Terminate the active mpv process, if any.

        Safe to call when no process is running.
        """
        if self._process is not None and self._process.poll() is None:
            self._process.terminate()
            try:
                self._process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self._process.kill()
                self._process.wait()
        self._process = None

    def is_playing(self) -> bool:
        """Return True while the mpv process is still alive."""
        return self._process is not None and self._process.poll() is None

    def wait(self) -> None:
        """Block until the current mpv process finishes naturally.

        Returns immediately if no process is active.
        Used by the playback loop when polling is not needed.
        """
        if self._process is not None:
            self._process.wait()
