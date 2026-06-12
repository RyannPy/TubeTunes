"""Player — mpv process wrapper with IPC-based control.

V1.0 capabilities:
  - Non-blocking Popen launch
  - IPC socket for seek / progress / pause
  - psutil suspend/resume as fallback if IPC is unavailable
"""

import sys
import uuid
import tempfile
import subprocess
import psutil
from pathlib import Path

from yt_dlp import YoutubeDL
from src.core.mpv_ipc import MpvIPC, IPCError


class PlaybackError(Exception):
    """Raised when audio stream extraction or mpv playback fails."""
    pass


def _make_ipc_path() -> str:
    """Return a unique IPC socket path appropriate for the platform."""
    if sys.platform == "win32":
        # Named Pipe — mpv creates it automatically
        uid = uuid.uuid4().hex[:8]
        return rf"\\.\pipe\tubetunes-{uid}"
    else:
        tmp = Path(tempfile.gettempdir())
        uid = uuid.uuid4().hex[:8]
        return str(tmp / f"tubetunes-{uid}.sock")


class Player:
    """Wraps mpv as a controllable subprocess with IPC.

    Launch flow:
        play(url)
          → resolves audio stream via yt-dlp
          → starts mpv with --input-ipc-server=<path>
          → connects MpvIPC
          → IPC used for: pause, resume, seek, get_position, get_duration

    Fallback:
        If IPC connection fails, psutil suspend/resume is used for
        pause/resume. Seek is unavailable without IPC.
    """

    def __init__(self):
        self._process: subprocess.Popen | None = None
        self._ipc: MpvIPC | None = None
        self._ipc_path: str = ""
        self._paused: bool = False
        self._ipc_ok: bool = False     # True once IPC connected successfully

    # ------------------------------------------------------------------
    # Stream resolution
    # ------------------------------------------------------------------

    def get_audio_stream(self, video_url: str) -> str:
        """Resolve the best audio stream URL via yt-dlp.

        Raises PlaybackError on failure.
        """
        ydl_opts = {"format": "bestaudio", "quiet": True}
        try:
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
        except Exception as e:
            raise PlaybackError(f"Could not extract audio stream: {e}") from e
        return info["url"]

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def play(self, video_url: str) -> None:
        """Resolve stream, launch mpv with IPC socket, connect IPC client.

        Raises PlaybackError if mpv is not installed.
        """
        audio_url = self.get_audio_stream(video_url)
        self._ipc_path = _make_ipc_path()
        self._paused = False
        self._ipc_ok = False

        try:
            self._process = subprocess.Popen(
                [
                    "mpv",
                    "--no-terminal",
                    f"--input-ipc-server={self._ipc_path}",
                    audio_url,
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except FileNotFoundError:
            raise PlaybackError(
                "mpv is not installed. Please install mpv to play audio."
            )
        except Exception as e:
            raise PlaybackError(f"Could not start mpv: {e}") from e

        # Connect IPC — mpv takes a moment to create the socket
        self._ipc = MpvIPC(self._ipc_path)
        try:
            self._ipc.connect(retries=25, delay=0.1)
            self._ipc_ok = True
        except IPCError:
            # IPC unavailable — playback still works, seek/progress won't
            self._ipc_ok = False

    def stop(self) -> None:
        """Terminate mpv, close IPC. Safe to call when nothing is running."""
        if self._ipc is not None:
            self._ipc.close()
            self._ipc = None
            self._ipc_ok = False

        if self._process is not None and self._process.poll() is None:
            if self._paused:
                self._psutil_resume()
            self._process.terminate()
            try:
                self._process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self._process.kill()
                self._process.wait()

        self._process = None
        self._paused = False

    def is_playing(self) -> bool:
        """True while mpv process is alive (includes paused state)."""
        return self._process is not None and self._process.poll() is None

    def is_paused(self) -> bool:
        """True if paused (via IPC or psutil)."""
        return self._paused and self.is_playing()

    # ------------------------------------------------------------------
    # Pause / Resume  (IPC-first, psutil fallback)
    # ------------------------------------------------------------------

    def pause(self) -> None:
        """Pause playback. No-op if already paused or not playing."""
        if not self.is_playing() or self._paused:
            return
        if self._ipc_ok and self._ipc:
            self._ipc.set_property("pause", True)
        else:
            self._psutil_suspend()
        self._paused = True

    def resume(self) -> None:
        """Resume playback. No-op if not paused."""
        if not self._paused:
            return
        if self._ipc_ok and self._ipc:
            self._ipc.set_property("pause", False)
        else:
            self._psutil_resume()
        self._paused = False

    def toggle_pause(self) -> bool:
        """Toggle pause state. Returns new paused state (True = paused)."""
        if self._paused:
            self.resume()
        else:
            self.pause()
        return self._paused

    # ------------------------------------------------------------------
    # Seek  (IPC only)
    # ------------------------------------------------------------------

    def seek(self, seconds: float) -> bool:
        """Seek relative to current position by `seconds` (+/-).

        Returns True if the seek command was sent, False if IPC unavailable.
        Does nothing when paused — seek while paused is deferred to V2.0.
        """
        if not self._ipc_ok or self._ipc is None:
            return False
        self._ipc.send_command("seek", seconds, "relative")
        return True

    # ------------------------------------------------------------------
    # Progress  (IPC only)
    # ------------------------------------------------------------------

    def get_position(self) -> float | None:
        """Return current playback position in seconds, or None."""
        if not self._ipc_ok or self._ipc is None:
            return None
        val = self._ipc.get_property("time-pos", timeout=0.3)
        try:
            return float(val) if val is not None else None
        except (TypeError, ValueError):
            return None

    def get_duration(self) -> float | None:
        """Return total track duration in seconds, or None."""
        if not self._ipc_ok or self._ipc is None:
            return None
        val = self._ipc.get_property("duration", timeout=0.3)
        try:
            return float(val) if val is not None else None
        except (TypeError, ValueError):
            return None

    # ------------------------------------------------------------------
    # psutil helpers (fallback / stop safety)
    # ------------------------------------------------------------------

    def _psutil_suspend(self) -> None:
        try:
            psutil.Process(self._process.pid).suspend()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    def _psutil_resume(self) -> None:
        try:
            psutil.Process(self._process.pid).resume()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
