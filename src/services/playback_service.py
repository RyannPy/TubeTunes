import sys
import time
import threading

from src.core.playlist_loader import load_playlist, PlaylistLoadError
from src.core.queue_manager import QueueManager
from src.core.player import Player, PlaybackError
from src.utils.console import console

# ---------------------------------------------------------------------------
# Platform-aware single-character input
# ---------------------------------------------------------------------------

if sys.platform == "win32":
    import msvcrt

    def _read_char() -> str | None:
        """Return a single character if one is waiting, else None (Windows)."""
        if msvcrt.kbhit():
            ch = msvcrt.getwch()
            return ch.lower()
        return None

else:
    import tty
    import termios
    import select

    def _read_char() -> str | None:
        """Return a single character if one is waiting, else None (Unix)."""
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ready, _, _ = select.select([sys.stdin], [], [], 0)
            if ready:
                return sys.stdin.read(1).lower()
            return None
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)


# ---------------------------------------------------------------------------
# Input reader thread
# ---------------------------------------------------------------------------

# Sentinel values written to the shared command slot by the input thread.
_CMD_NEXT = "n"
_CMD_PREV = "p"
_CMD_QUIT = "q"
_VALID_CMDS = {_CMD_NEXT, _CMD_PREV, _CMD_QUIT}

# Module-level shared state between the input thread and the playback loop.
# A plain string slot is sufficient — only one command is acted on per
# poll cycle, and we reset it after reading.
_pending_command: str | None = None
_input_active: bool = False
_input_lock = threading.Lock()


def _input_worker() -> None:
    """Daemon thread: poll stdin for n/p/q and store in _pending_command."""
    global _pending_command, _input_active

    while _input_active:
        ch = _read_char()
        if ch in _VALID_CMDS:
            with _input_lock:
                _pending_command = ch
        time.sleep(0.05)  # 50 ms poll — low CPU, responsive enough


def _start_input_thread() -> threading.Thread:
    global _input_active
    _input_active = True
    t = threading.Thread(target=_input_worker, daemon=True)
    t.start()
    return t


def _stop_input_thread() -> None:
    global _input_active
    _input_active = False


def _take_command() -> str | None:
    """Consume and return any pending command, or None."""
    global _pending_command
    with _input_lock:
        cmd = _pending_command
        _pending_command = None
    return cmd


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

def _print_now_playing(queue: QueueManager) -> None:
    console.rule("TubeTunes")
    console.print(f"[green]▶ {queue.current_title()}[/green]")

    upcoming = queue.upcoming()
    if upcoming:
        console.print("[cyan]\nNext Up:[/cyan]")
        for i, song in enumerate(upcoming, start=1):
            console.print(f"[cyan]{i}. {song['title']}[/cyan]")

    console.print(
        "\n[dim]Controls:  "
        "[bold]n[/bold] = next   "
        "[bold]p[/bold] = previous   "
        "[bold]q[/bold] = quit[/dim]\n"
    )


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def play_playlist(playlist_url: str, shuffle: bool = False) -> None:
    """Full playback workflow: load → queue → controller loop → play.

    Replaces the old blocking subprocess.run approach with a Popen-based
    controller that responds to n / p / q keypresses while music plays.

    V3.1 extension point: add pause/resume by calling player.pause() here
    and adding 'space' to _VALID_CMDS.
    """
    # ---- Load ----
    try:
        playlist = load_playlist(playlist_url)
    except PlaylistLoadError as e:
        console.print(f"[red]Error loading playlist:[/red] {e}")
        return

    entries = playlist.get("entries") or []
    if not entries:
        console.print("[red]Playlist is empty — nothing to play.[/red]")
        return

    # ---- Build queue ----
    queue = QueueManager(entries, shuffle=shuffle)
    player = Player()

    mode_label = "[magenta]Shuffle[/magenta]" if shuffle else "[white]Normal[/white]"
    console.print(f"[dim]Playback mode:[/dim] {mode_label}\n")

    # ---- Start input thread ----
    _start_input_thread()

    try:
        _run_controller(queue, player)
    except KeyboardInterrupt:
        console.print("\n[yellow]Stopping playback...[/yellow]")
        player.stop()
    finally:
        _stop_input_thread()


# ---------------------------------------------------------------------------
# Controller loop  (internal)
# ---------------------------------------------------------------------------

def _run_controller(queue: QueueManager, player: Player) -> None:
    """Drive the queue-player loop, reacting to n / p / q commands.

    The loop structure:
      1. Start playing current song (non-blocking Popen).
      2. Poll every 100 ms: check if song ended naturally OR a command arrived.
      3. Act on command (next / previous / quit) or advance automatically.
    """
    while queue.has_next():
        _print_now_playing(queue)

        try:
            player.play(queue.current_url())
        except PlaybackError as e:
            console.print(f"[red]Playback error:[/red] {e}")
            queue.advance()
            continue

        # ---- Poll loop: song is now playing in the background ----
        action = _poll_until_done(player)

        if action == _CMD_QUIT:
            player.stop()
            console.print("[yellow]Stopping playback...[/yellow]")
            return

        if action == _CMD_NEXT:
            player.stop()
            if queue.has_next():
                queue.advance()
                # has_next() re-checked at top of while — handles end-of-queue
                if not queue.has_next():
                    console.print("[dim]End of playlist.[/dim]")
                    return
            else:
                console.print("[dim]End of playlist.[/dim]")
                return
            continue

        if action == _CMD_PREV:
            player.stop()
            if queue.has_previous():
                queue.back()
            else:
                console.print("[yellow]Already at first song.[/yellow]")
            # replay current (index unchanged if at start)
            continue

        # action is None → song finished naturally
        queue.advance()

    console.print("[dim]End of playlist.[/dim]")


def _poll_until_done(player: Player) -> str | None:
    """Block until mpv exits or a command key is pressed.

    Returns the command string ('n', 'p', 'q') or None if the song
    finished on its own.
    """
    while player.is_playing():
        cmd = _take_command()
        if cmd in _VALID_CMDS:
            return cmd
        time.sleep(0.1)

    # Song ended naturally — drain any stale command that arrived at the
    # exact moment the process exited, so it does not bleed into the next
    # song's poll cycle.
    _take_command()
    return None
