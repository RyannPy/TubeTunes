from src.core.playlist_loader import load_playlist, PlaylistLoadError
from src.core.queue_manager import QueueManager
from src.core.player import Player, PlaybackError
from src.utils.console import console


def play_playlist(playlist_url: str, shuffle: bool = False) -> None:
    """Full playback workflow: load → queue → display → play.

    Args:
        playlist_url: A direct YouTube playlist URL.
        shuffle: Whether to shuffle the queue before playing.

    KeyboardInterrupt is caught here so playback can be stopped cleanly
    with Ctrl+C without surfacing a Python traceback.

    V3.0 extension point: replace the inner while-loop with a controller
    object that supports next/previous/pause via mpv IPC or threading.
    """
    # Load playlist entries from YouTube
    try:
        playlist = load_playlist(playlist_url)
    except PlaylistLoadError as e:
        console.print(f"[red]Error loading playlist:[/red] {e}")
        return

    entries = playlist.get("entries") or []
    if not entries:
        console.print("[red]Playlist is empty — nothing to play.[/red]")
        return

    # Build the queue
    queue = QueueManager(entries, shuffle=shuffle)

    player = Player()

    mode_label = "[magenta]Shuffle[/magenta]" if shuffle else "[white]Normal[/white]"
    console.print(f"[dim]Playback mode:[/dim] {mode_label}\n")

    # Play through the queue
    try:
        while queue.has_next():
            console.rule("TubeTunes")

            console.print(f"[green]▶ {queue.current_title()}[/green]")

            upcoming = queue.upcoming()
            if upcoming:
                console.print("[cyan]\nNext Up:[/cyan]")
                for i, song in enumerate(upcoming, start=1):
                    console.print(f"[cyan]{i}. {song['title']}[/cyan]")

            try:
                player.play(queue.current_url())
            except PlaybackError as e:
                console.print(f"[red]Playback error:[/red] {e}")

            queue.advance()

    except KeyboardInterrupt:
        console.print("\n[yellow]Stopping playback...[/yellow]")
