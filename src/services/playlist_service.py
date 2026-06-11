from src.storage.playlist_storage import load_all, save_all


def save_alias(alias: str, url: str) -> None:
    """Save a playlist alias pointing to the given URL."""
    playlists = load_all()
    playlists[alias] = url
    save_all(playlists)


def get_url(alias: str):
    """Resolve an alias to its stored URL.
    Returns the URL string, or None if the alias does not exist.
    """
    playlists = load_all()
    return playlists.get(alias)


def list_aliases() -> dict:
    """Return all saved alias → URL mappings."""
    return load_all()


def resolve_playlist_url(input_str: str):
    """Resolve a raw user input to a playlist URL.

    If the input looks like a URL (starts with 'http'), return it as-is.
    Otherwise treat it as an alias and look it up in storage.
    Returns the URL string, or None if the alias is not found.
    """
    if input_str.startswith("http"):
        return input_str
    return get_url(input_str)
