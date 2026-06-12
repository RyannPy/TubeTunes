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


def delete_alias(alias: str) -> None:
    """Remove a playlist alias from storage.

    Raises KeyError if the alias does not exist.
    """
    playlists = load_all()
    if alias not in playlists:
        raise KeyError(f"Alias not found: '{alias}'")
    del playlists[alias]
    save_all(playlists)


def rename_alias(old_alias: str, new_alias: str) -> None:
    """Rename an existing alias to a new name, preserving its URL.

    Raises KeyError  if old_alias does not exist.
    Raises ValueError if new_alias is empty, whitespace-only, or already taken.
    """
    new_alias = new_alias.strip()

    if not new_alias:
        raise ValueError("New alias cannot be empty.")

    playlists = load_all()

    if old_alias not in playlists:
        raise KeyError(f"Alias not found: '{old_alias}'")

    if new_alias in playlists:
        raise ValueError(f"Alias already exists: '{new_alias}'")

    # Preserve insertion order: rebuild dict with the key renamed in-place
    updated = {}
    for key, value in playlists.items():
        if key == old_alias:
            updated[new_alias] = value
        else:
            updated[key] = value

    save_all(updated)


def resolve_playlist_url(input_str: str):
    """Resolve a raw user input to a playlist URL.

    If the input looks like a URL (starts with 'http'), return it as-is.
    Otherwise treat it as an alias and look it up in storage.
    Returns the URL string, or None if the alias is not found.
    """
    if input_str.startswith("http"):
        return input_str
    return get_url(input_str)
