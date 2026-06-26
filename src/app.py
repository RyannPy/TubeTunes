from src.cli.cli import parse_args
from src.cli.menu import handle_menu
from src.services.playlist_service import resolve_playlist_url, save_alias
from src.services.playback_service import play_playlist
from src.utils.console import console


def main():
    try:
        _run()
    except KeyboardInterrupt:
        console.print("\n[yellow]Exiting TubeTunes. Goodbye![/yellow]")


def _run():
    args = parse_args()

    if args.command == "save":
        save_alias(args.alias, args.playlist_url)
        console.print(f"[green]Saved:[/green] {args.alias}")
        return

    if args.command is None:
        handle_menu()
        return

    # "play" command
    playlist_url = resolve_playlist_url(args.playlist_url)

    if playlist_url is None:
        console.print(f"[red]Alias not found:[/red] '{args.playlist_url}'")
        return

    play_playlist(
        playlist_url,
        playlist_alias=args.playlist_url,
        shuffle=args.shuffle,
    )


if __name__ == "__main__":
    main()
