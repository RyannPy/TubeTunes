import questionary
from src.services.playlist_service import save_alias, list_aliases
from src.services.playback_service import play_playlist
from src.utils.console import console


# ---------------------------------------------------------------------------
# Low-level prompt helpers
# ---------------------------------------------------------------------------

def show_menu() -> str:
    """Show the main menu and return the user's choice."""
    return questionary.select(
        "TubeTunes",
        choices=[
            "Play Playlist",
            "Add Playlist",
            "List Playlists",
            "Exit",
        ],
    ).ask()


def ask_alias() -> str:
    return questionary.text("Alias:").ask()


def ask_url() -> str:
    return questionary.text("Playlist URL:").ask()


def choose_playlist(playlists: dict) -> str:
    """Present a selection list of saved aliases; return the chosen alias."""
    return questionary.select(
        "Choose Playlist",
        choices=list(playlists.keys()),
    ).ask()


# ---------------------------------------------------------------------------
# High-level menu handler
# ---------------------------------------------------------------------------

def handle_menu() -> None:
    """Drive the interactive menu decision tree."""
    choice = show_menu()

    if choice == "Exit" or choice is None:
        return

    if choice == "List Playlists":
        playlists = list_aliases()

        if not playlists:
            console.print("[yellow]No saved playlists yet.[/yellow]")
            return

        console.rule("Saved Playlists")
        for alias in playlists:
            console.print(f"[cyan]{alias}[/cyan]")
        return

    if choice == "Add Playlist":
        alias = ask_alias()
        url = ask_url()
        save_alias(alias, url)
        console.print(f"[green]Saved:[/green] {alias}")
        return

    if choice == "Play Playlist":
        playlists = list_aliases()

        if not playlists:
            console.print("[yellow]No saved playlists yet.[/yellow]")
            return

        alias = choose_playlist(playlists)
        if alias is None:
            return

        playlist_url = playlists[alias]
        play_playlist(playlist_url)
