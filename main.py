from queue_manager import QueueManager
from player import Player
from rich.console import Console
from cli import parse_args
from playlist import get_playlist
from storage_playlist import (
    save_playlist,
    get_playlist_url,
)

console = Console()

# parse input
args = parse_args()

if args.command == "save":

    save_playlist(
        args.alias,
        args.playlist_url
    )

    console.print(
        f"[green]Saved:[/green] {args.alias}"
    )

    exit()


# get url dan playlist
if args.playlist_url.startswith("http"):

    playlist_url = args.playlist_url

else:

    playlist_url = get_playlist_url(
        args.playlist_url
    )


if playlist_url is None:

    console.print(
        "[red]Playlist alias not found[/red]"
    )

    exit()

# ambil lagu yt
playlist = get_playlist(
    playlist_url
)

# manage queue
queue = QueueManager(
    playlist["entries"],
    shuffle=args.shuffle

)

player = Player()

# play songs
while queue.has_next():

    try:
        console.rule("TubeTunes")

        # TITLE
        console.print(f"[green]▶ {queue.current_title()}[/green]")

        # COMING UP
        console.print("[cyan]\nNext Up:[/cyan]")
        for i, song in enumerate(
            queue.upcoming(),
            start=1
        ):
            console.print(f"[cyan]{i}. {song['title']}[/cyan]")

        # PLAY
        player.play(queue.current_url())

    except Exception as e:

        console.print(f"Error: {e}")

    queue.advance()