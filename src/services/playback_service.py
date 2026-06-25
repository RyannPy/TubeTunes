"""Playback service — controller loop with Rich Live UI.

V1.0 controls:
    n     = next song
    p     = previous song
    space = pause / resume
    f     = seek forward  +10 s
    b     = seek backward -10 s
    q     = quit playback (return to menu)
"""

import sys
import time
import threading

from rich.align import Align
from rich.columns import Columns
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from src.core.playlist_loader import load_playlist, PlaylistLoadError
from src.core.queue_manager import QueueManager
from src.core.player import Player, PlaybackError
from src.utils.console import console

from src.services.discord_rpc import (
    connect,
    update_song,
    close,
)
# ---------------------------------------------------------------------------
# Platform-aware single-character input
# ---------------------------------------------------------------------------

if sys.platform == "win32":
    import msvcrt

    def _read_char() -> str | None:
        if msvcrt.kbhit():
            ch = msvcrt.getwch()
            return " " if ch == " " else ch.lower()
        return None

else:
    import tty
    import termios
    import select

    def _read_char() -> str | None:
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ready, _, _ = select.select([sys.stdin], [], [], 0)
            if ready:
                ch = sys.stdin.read(1)
                return " " if ch == " " else ch.lower()
            return None
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)


# ---------------------------------------------------------------------------
# Input thread
# ---------------------------------------------------------------------------

_CMD_NEXT    = "n"
_CMD_PREV    = "p"
_CMD_QUIT    = "q"
_CMD_PAUSE   = " "
_CMD_SEEK_F  = "f"
_CMD_SEEK_B  = "b"
_VALID_CMDS  = {_CMD_NEXT, _CMD_PREV, _CMD_QUIT, _CMD_PAUSE, _CMD_SEEK_F, _CMD_SEEK_B}

_pending_command: str | None = None
_input_active: bool = False
_input_lock = threading.Lock()

SEEK_SECONDS = 10   # seconds per f/b keypress


def _input_worker() -> None:
    global _pending_command, _input_active
    while _input_active:
        ch = _read_char()
        if ch in _VALID_CMDS:
            with _input_lock:
                _pending_command = ch
        time.sleep(0.05)


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
    global _pending_command
    with _input_lock:
        cmd = _pending_command
        _pending_command = None
    return cmd


# ---------------------------------------------------------------------------
# Time formatting
# ---------------------------------------------------------------------------

def _fmt_time(seconds: float | None) -> str:
    """Format seconds as MM:SS. Returns --:-- if None."""
    if seconds is None:
        return "--:--"
    seconds = max(0.0, seconds)
    m = int(seconds) // 60
    s = int(seconds) % 60
    return f"{m:02d}:{s:02d}"


# ---------------------------------------------------------------------------
# Rich UI builder
# ---------------------------------------------------------------------------

def _build_playback_panel(
    queue: QueueManager,
    paused: bool,
    position: float | None,
    duration: float | None,
    status_msg: str,
    ipc_ok: bool,
) -> Panel:
    """Build the full Rich panel rendered by Live on every tick."""

    # ── Now Playing ──────────────────────────────────────────────────
    title_text = Text(queue.current_title(), style="bold green")
    now_playing = Align.center(title_text)

    # ── Status row ───────────────────────────────────────────────────
    if paused:
        state_str = Text("⏸  PAUSED", style="bold yellow")
    else:
        state_str = Text("▶  PLAYING", style="bold green")

    progress_str = Text(
        f"{_fmt_time(position)}  /  {_fmt_time(duration)}",
        style="cyan",
    )

    status_table = Table.grid(padding=(0, 3))
    status_table.add_column(justify="center")
    status_table.add_column(justify="center")
    status_table.add_row(state_str, progress_str)

    # ── Feedback message (seek / pause confirmation) ──────────────────
    msg_line = Text(status_msg, style="dim italic") if status_msg else Text("")

    # ── Upcoming queue ────────────────────────────────────────────────
    upcoming = queue.upcoming(limit=3)
    if upcoming:
        queue_table = Table(
            show_header=True,
            header_style="bold cyan",
            box=None,
            padding=(0, 1),
        )
        queue_table.add_column("#", style="dim", width=3, justify="right")
        queue_table.add_column("Up Next", style="white")
        for i, song in enumerate(upcoming, start=1):
            queue_table.add_row(str(i), song["title"])
    else:
        queue_table = Text("[dim]End of playlist[/dim]")

    # ── Controls ─────────────────────────────────────────────────────
    seek_note = "" if ipc_ok else "  [dim](seek unavailable — IPC not connected)[/dim]"
    controls_table = Table.grid(padding=(0, 2))
    controls_table.add_column(style="bold white", justify="right", width=7)
    controls_table.add_column(style="dim")
    controls_table.add_row("SPACE", "Pause / Resume")
    controls_table.add_row("N", "Next song")
    controls_table.add_row("P", "Previous song")
    controls_table.add_row("F", f"+{SEEK_SECONDS}s{seek_note}")
    controls_table.add_row("B", f"-{SEEK_SECONDS}s")
    controls_table.add_row("Q", "Quit playback")

    # ── Assemble layout ───────────────────────────────────────────────
    layout = Table.grid(padding=(0, 0))
    layout.add_column()
    layout.add_row("")
    layout.add_row(Align.center(now_playing))
    layout.add_row("")
    layout.add_row(Align.center(status_table))
    if status_msg:
        layout.add_row(Align.center(msg_line))
    layout.add_row("")
    if upcoming:
        layout.add_row(Align.center(queue_table))
        layout.add_row("")
    layout.add_row(Align.center(controls_table))
    layout.add_row("")

    return Panel(
        layout,
        title="[bold cyan]TubeTunes[/bold cyan]",
        border_style="cyan",
        expand=False,
    )


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def play_playlist(playlist_url: str, shuffle: bool = False) -> None:
    """Full playback workflow: load → queue → controller loop."""
    try:
        playlist = load_playlist(playlist_url)
    except PlaylistLoadError as e:
        console.print(f"[red]Error loading playlist:[/red] {e}")
        return

    entries = playlist.get("entries") or []
    if not entries:
        console.print("[red]Playlist is empty — nothing to play.[/red]")
        return

    queue  = QueueManager(entries, shuffle=shuffle)
    player = Player()

    # connect to discord
    connect()

    mode_label = "[magenta]Shuffle[/magenta]" if shuffle else "[white]Normal[/white]"
    console.print(f"[dim]Playback mode:[/dim] {mode_label}\n")

    _start_input_thread()
    try:
        _run_controller(queue, player)
    except KeyboardInterrupt:
        console.print("\n[yellow]Stopping playback...[/yellow]")
        player.stop()
    finally:
        # disconnect from discord
        close()
        # stop
        _stop_input_thread()


# ---------------------------------------------------------------------------
# Controller loop
# ---------------------------------------------------------------------------

def _run_controller(queue: QueueManager, player: Player) -> None:
    """Drive the queue-player loop with Rich Live UI."""
    # Live context persists across songs so the panel updates in place
    live_console = Console()

    with Live(
        console=live_console,
        refresh_per_second=4,
        screen=False,
        transient=False,
    ) as live:
        while queue.has_next():
            try:
                # update discord
                update_song(
                    queue.current_title(),
                    paused=False,
                )

                # play
                player.play(queue.current_url())
            except PlaybackError as e:
                console.print(f"[red]Playback error:[/red] {e}")
                queue.advance()
                continue

            action = _poll_until_done(player, queue, live)

            if action == _CMD_QUIT:
                player.stop()
                live.stop()
                console.print("[yellow]Stopping playback...[/yellow]")
                return

            if action == _CMD_NEXT:
                player.stop()
                queue.advance()
                if not queue.has_next():
                    live.stop()
                    console.print("[dim]End of playlist.[/dim]")
                    return
                continue

            if action == _CMD_PREV:
                player.stop()
                if queue.has_previous():
                    queue.back()
                else:
                    console.print("[yellow]Already at first song.[/yellow]")
                continue

            # Natural end → advance
            queue.advance()

    console.print("[dim]End of playlist.[/dim]")


# ---------------------------------------------------------------------------
# Poll loop
# ---------------------------------------------------------------------------

def _poll_until_done(
    player: Player,
    queue: QueueManager,
    live: Live,
) -> str | None:
    """Poll until mpv exits or a navigation/quit key is pressed.

    Space   → toggle pause in-place, update UI, keep polling.
    F / B   → seek ±10 s, update UI, keep polling.
    N/P/Q   → return the command to the controller.
    None    → song ended naturally.
    """
    status_msg = ""
    msg_clear_at: float = 0.0       # monotonic time when to clear the message

    while player.is_playing():
        cmd = _take_command()

        # ── Seek forward ───────────────────────────────────────────────
        if cmd == _CMD_SEEK_F:
            if player.seek(SEEK_SECONDS):
                status_msg = f"+{SEEK_SECONDS}s"
            else:
                status_msg = "seek unavailable"
            msg_clear_at = time.monotonic() + 1.5

        # ── Seek backward ──────────────────────────────────────────────
        elif cmd == _CMD_SEEK_B:
            if player.seek(-SEEK_SECONDS):
                status_msg = f"-{SEEK_SECONDS}s"
            else:
                status_msg = "seek unavailable"
            msg_clear_at = time.monotonic() + 1.5

        # ── Pause / Resume ─────────────────────────────────────────────
        elif cmd == _CMD_PAUSE:
            now_paused = player.toggle_pause()
            # update discord
            update_song(
                queue.current_title(),
                paused=now_paused,
            )
            
            status_msg = "Paused" if now_paused else "Resumed"
            msg_clear_at = time.monotonic() + 1.5

        # ── Navigation / Quit — hand off to controller ─────────────────
        elif cmd in {_CMD_NEXT, _CMD_PREV, _CMD_QUIT}:
            if player.is_paused():
                player.resume()
            return cmd

        # ── Clear timed message ────────────────────────────────────────
        if status_msg and time.monotonic() > msg_clear_at:
            status_msg = ""

        # ── Update Live UI ─────────────────────────────────────────────
        pos = player.get_position()
        dur = player.get_duration()
        live.update(
            _build_playback_panel(
                queue=queue,
                paused=player.is_paused(),
                position=pos,
                duration=dur,
                status_msg=status_msg,
                ipc_ok=player._ipc_ok,
            )
        )

        time.sleep(0.1)

    # Song ended naturally
    _take_command()
    return None
