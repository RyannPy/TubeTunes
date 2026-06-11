from yt_dlp import YoutubeDL


class PlaylistLoadError(Exception):
    """Raised when a playlist cannot be loaded from the given URL."""
    pass


def load_playlist(url: str) -> dict:
    """Fetch playlist metadata from YouTube via yt-dlp.

    Returns the full info dict from yt-dlp.
    Raises PlaylistLoadError if the URL is invalid, unreachable,
    or the resulting playlist is empty.
    """
    ydl_opts = {
        "quiet": True,
        "extract_flat": True,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
    except Exception as e:
        raise PlaylistLoadError(
            f"Could not load playlist. Check the URL.\n({e})"
        ) from e

    if not info or not info.get("entries"):
        raise PlaylistLoadError(
            "Playlist is empty or could not be loaded."
        )

    return info
