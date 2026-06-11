import json
from pathlib import Path

PLAYLIST_FILE = Path(
    "data/playlists.json"
)


def load_all():

    with open(
        PLAYLIST_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


def save_all(data):

    with open(
        PLAYLIST_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            indent=4
        )

def save_playlist(
    alias,
    url
):

    playlists = load_all()

    playlists[alias] = url

    save_all(playlists)

def get_playlist_url(
    alias
):

    playlists = load_all()

    return playlists.get(alias)

def list_playlists():

    playlists = load_all()

    return playlists