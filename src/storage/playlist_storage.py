import json
from pathlib import Path

PLAYLIST_FILE = Path("data/playlists.json")


def load_all() -> dict:
    """Read data/playlists.json and return its contents as a dict.
    Creates the file with an empty dict if it does not exist.
    """
    if not PLAYLIST_FILE.exists():
        PLAYLIST_FILE.parent.mkdir(parents=True, exist_ok=True)
        save_all({})
        return {}

    with open(PLAYLIST_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_all(data: dict) -> None:
    """Write a dict to data/playlists.json.
    Creates the data/ directory if it does not exist.
    """
    PLAYLIST_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(PLAYLIST_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
