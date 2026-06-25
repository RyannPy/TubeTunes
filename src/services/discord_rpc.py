from pypresence import Presence
import time

APP_ID = "1519532503055208458"

_rpc = None


def connect():
    global _rpc

    try:
        _rpc = Presence(APP_ID)
        _rpc.connect()
        return True
    except Exception:
        _rpc = None
        return False


def update_song(title: str, paused: bool = False):
    if _rpc is None:
        return

    if len(title) > 50:
        title = title[:47] + "..."

    try:
        _rpc.update(
            details=title,
            state="Paused" if paused else "Listening with TubeTunes",
            large_image="tubetunes",
            large_text="TubeTunes",
            small_image="pause" if paused else "play",
            small_text="Paused" if paused else "Playing",
        )
    except Exception:
        pass


def close():
    global _rpc

    if _rpc is None:
        return

    try:
        _rpc.close()
    except Exception:
        pass

    _rpc = None