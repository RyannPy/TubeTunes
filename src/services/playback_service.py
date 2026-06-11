from src.core.playlist_loader import load_playlist, PlaylistLoadError
from src.core.queue_manager import QueueManager
from src.core.player import Player, PlaybackError
from src.utils.console import console


def play_playlist(playlist_url: str, shuffle: bool = False) -> None:
    """Full playback workflow: load → queue → display → play.

    Args:
        playlist_url: A direct YouTube playlist URL.
        shuffle: Whether to shuffle the queue before playing.
    """
    # Load playlist entries from YouTube
    try:
        playlist = load_playlist(playlist_url)
    except PlaylistLoadError as e:
        console.print(f"[red]{e}[/red]")
        return

    # Build the queue
    queue = QueueManager(playlist["entries"], shuffle=shuffle)

    player = Player()

    # Play through the queue
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
            console.print(f"[red]Playback error: {e}[/red]")

        queue.advance()
