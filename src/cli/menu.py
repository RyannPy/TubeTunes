import questionary
from src.services.playlist_service import (
    save_alias,
    list_aliases,
    delete_alias,
    rename_alias,
)
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
            "Rename Playlist",
            "Delete Playlist",
            "Exit",
        ],
    ).ask()


def ask_alias() -> str:
    return questionary.text("Alias:").ask()


def ask_url() -> str:
    return questionary.text("Playlist URL:").ask()


def ask_new_alias() -> str:
    return questionary.text("New alias:").ask()


def choose_playlist(playlists: dict) -> str:
    """Present a selection list of saved aliases; return the chosen alias."""
    return questionary.select(
        "Choose Playlist",
        choices=list(playlists.keys()),
    ).ask()


def choose_playlist_for_action(playlists: dict, prompt: str = "Choose Playlist") -> str:
    """Present a labelled selection list; return the chosen alias.

    Accepts a custom prompt label so Delete and Rename can identify themselves.
    """
    return questionary.select(
        prompt,
        choices=list(playlists.keys()),
    ).ask()


def confirm_delete(alias: str) -> bool:
    """Ask the user to confirm deletion of an alias. Returns True to proceed."""
    return questionary.confirm(f'Delete "{alias}"?', default=False).ask()


def choose_playback_mode() -> bool:
    """Ask the user to select Normal or Shuffle playback.

    Returns True if Shuffle was chosen, False for Normal.
    Returns False (Normal) if the prompt is cancelled (Ctrl+C / None).
    """
    choice = questionary.select(
        "Playback Mode",
        choices=["Normal", "Shuffle"],
    ).ask()
    return choice == "Shuffle"


def pause_for_continue() -> None:
    """Pause and wait for the user to press Enter before returning to menu."""
    questionary.press_any_key_to_continue("Press Enter to continue...").ask()


# ---------------------------------------------------------------------------
# Shared guard
# ---------------------------------------------------------------------------

def _require_playlists() -> dict | None:
    """Load aliases and return them, or print a notice and return None."""
    playlists = list_aliases()
    if not playlists:
        console.print("[yellow]No playlists saved.[/yellow]")
        pause_for_continue()
        return None
    return playlists


# ---------------------------------------------------------------------------
# Action handlers  (each performs one action and returns to the caller)
# ---------------------------------------------------------------------------

def _handle_list_playlists() -> None:
    """List all saved playlists, then wait for user to continue."""
    playlists = list_aliases()

    if not playlists:
        console.print("[yellow]No playlists saved.[/yellow]")
    else:
        console.rule("Saved Playlists")
        for alias, url in playlists.items():
            console.print(f"  [cyan]{alias}[/cyan]  [dim]{url}[/dim]")

    pause_for_continue()


def _handle_add_playlist() -> None:
    """Prompt for alias + URL, validate, save, then wait for user to continue."""
    alias = ask_alias()
    if alias is None:
        return
    url = ask_url()
    if url is None:
        return

    alias = alias.strip()
    url = url.strip()

    if not alias:
        console.print("[red]Alias cannot be empty.[/red]")
        pause_for_continue()
        return

    if not url:
        console.print("[red]URL cannot be empty.[/red]")
        pause_for_continue()
        return

    existing = list_aliases()
    if alias in existing:
        console.print(f"[red]Alias already exists:[/red] [cyan]{alias}[/cyan]")
        pause_for_continue()
        return

    save_alias(alias, url)
    console.print(f"[green]Playlist saved:[/green] [cyan]{alias}[/cyan]")
    pause_for_continue()


def _handle_play_playlist() -> None:
    """Let user choose a playlist and playback mode, then start playback."""
    playlists = _require_playlists()
    if playlists is None:
        return

    alias = choose_playlist(playlists)
    if alias is None:
        return

    shuffle = choose_playback_mode()
    if shuffle is None:
        return

    playlist_url = playlists[alias]
    play_playlist(playlist_url, shuffle=shuffle)


def _handle_rename_playlist() -> None:
    """Choose an alias, enter a new name, validate, then rename."""
    playlists = _require_playlists()
    if playlists is None:
        return

    old_alias = choose_playlist_for_action(playlists, prompt="Rename — Choose Playlist")
    if old_alias is None:
        return

    new_alias = ask_new_alias()
    if new_alias is None:
        return

    try:
        rename_alias(old_alias, new_alias)
    except ValueError as e:
        console.print(f"[red]{e}[/red]")
        pause_for_continue()
        return
    except KeyError as e:
        console.print(f"[red]{e}[/red]")
        pause_for_continue()
        return

    console.print(
        f"[green]Alias renamed:[/green] [cyan]{old_alias}[/cyan] → [cyan]{new_alias.strip()}[/cyan]"
    )
    pause_for_continue()


def _handle_delete_playlist() -> None:
    """Choose an alias, confirm, then delete."""
    playlists = _require_playlists()
    if playlists is None:
        return

    alias = choose_playlist_for_action(playlists, prompt="Delete — Choose Playlist")
    if alias is None:
        return

    confirmed = confirm_delete(alias)
    if not confirmed:
        console.print("[dim]Cancelled.[/dim]")
        pause_for_continue()
        return

    try:
        delete_alias(alias)
    except KeyError as e:
        console.print(f"[red]{e}[/red]")
        pause_for_continue()
        return

    console.print(f"[green]Playlist deleted:[/green] [cyan]{alias}[/cyan]")
    pause_for_continue()


# ---------------------------------------------------------------------------
# High-level menu handler  (menu loop — stays open until Exit)
# ---------------------------------------------------------------------------

def handle_menu() -> None:
    """Drive the interactive menu loop.

    Keeps showing the main menu until the user selects Exit or presses Ctrl+C.
    """
    while True:
        try:
            choice = show_menu()
        except KeyboardInterrupt:
            console.print("\n[yellow]Exiting TubeTunes. Goodbye![/yellow]")
            return

        if choice == "Exit" or choice is None:
            console.print("[dim]Goodbye![/dim]")
            return

        try:
            if choice == "List Playlists":
                _handle_list_playlists()

            elif choice == "Add Playlist":
                _handle_add_playlist()

            elif choice == "Play Playlist":
                _handle_play_playlist()

            elif choice == "Rename Playlist":
                _handle_rename_playlist()

            elif choice == "Delete Playlist":
                _handle_delete_playlist()

        except KeyboardInterrupt:
            console.print("\n[yellow]Returning to main menu...[/yellow]")
