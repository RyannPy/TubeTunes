import argparse


def parse_args():
    parser = argparse.ArgumentParser(
        prog="tubetunes"
    )

    subparsers = parser.add_subparsers(
        dest="command"
    )

    play_parser = subparsers.add_parser(
        "play"
    )

    play_parser.add_argument(
        "playlist_url"
    )
    
    play_parser.add_argument(
    "--shuffle",
    action="store_true"
)

    return parser.parse_args()