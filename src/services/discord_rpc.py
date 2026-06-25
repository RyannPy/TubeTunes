from pypresence import Presence


APP_ID = "1519532503055208458"

_rpc = None


def connect():
    """Connect to Discord Rich Presence."""
    global _rpc

    try:
        _rpc = Presence(APP_ID)
        _rpc.connect()
        return True
    
    except Exception as e:
        print("Discord RPC Error:", repr(e))

    _rpc = None
    return False


def update_song(title: str):
    """Update currently playing song."""
    if _rpc is None:
        return

    if len(title) > 50:
        title = title[:47] + "..."

    try:
        _rpc.update(
            details=title,
            state="Listening with TubeTunes",
        )
    except Exception:
        pass


def close():
    """Close Discord RPC connection."""
    global _rpc

    if _rpc is None:
        return

    try:
        _rpc.close()
    except Exception:
        pass

    _rpc = None