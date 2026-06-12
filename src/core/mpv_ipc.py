"""Minimal mpv IPC client.

Communicates with a running mpv process over its JSON IPC socket.

On Windows, mpv uses a Named Pipe:  \\\\.\\pipe\\<name>
On Unix,   mpv uses a Unix socket:  /tmp/<name>

Only the subset of the IPC protocol needed for TubeTunes is implemented:
  - send_command()   — fire-and-forget mpv commands
  - get_property()   — read a single mpv property
  - set_property()   — write a single mpv property

Future extension points:
  - observe_property() for event-driven progress updates  (V2.0)
  - request_id correlation for reliable responses          (V2.0)
"""

import json
import sys
import time


class IPCError(Exception):
    """Raised when the IPC connection cannot be established or used."""
    pass


class MpvIPC:
    """Thin wrapper around the mpv JSON IPC protocol."""

    def __init__(self, socket_path: str):
        self._path = socket_path
        self._conn = None   # platform file-like object

    # ------------------------------------------------------------------
    # Connection lifecycle
    # ------------------------------------------------------------------

    def connect(self, retries: int = 20, delay: float = 0.1) -> None:
        """Open the IPC socket/pipe, retrying until mpv creates it.

        Raises IPCError if the socket is not available after all retries.
        """
        for _ in range(retries):
            try:
                if sys.platform == "win32":
                    # Named Pipe — open in binary, unbuffered read/write
                    self._conn = open(self._path, "r+b", buffering=0)  # noqa: WPS515
                else:
                    import socket as _socket
                    s = _socket.socket(_socket.AF_UNIX, _socket.SOCK_STREAM)
                    s.connect(self._path)
                    self._conn = s.makefile("rwb", buffering=0)
                return
            except (FileNotFoundError, OSError):
                time.sleep(delay)

        raise IPCError(
            f"Could not connect to mpv IPC socket at '{self._path}'. "
            "Is mpv running with --input-ipc-server?"
        )

    def close(self) -> None:
        """Close the IPC connection. Safe to call when already closed."""
        if self._conn is not None:
            try:
                self._conn.close()
            except OSError:
                pass
            self._conn = None

    # ------------------------------------------------------------------
    # Low-level send / receive
    # ------------------------------------------------------------------

    def _send(self, payload: dict) -> None:
        """Serialise payload to JSON and write it to the pipe/socket."""
        if self._conn is None:
            return
        line = json.dumps(payload) + "\n"
        try:
            self._conn.write(line.encode())
        except OSError:
            pass

    def _read_response(self, timeout: float = 0.3) -> dict | None:
        """Read one JSON line from the pipe/socket within timeout seconds.

        Returns the parsed dict, or None on timeout / error.
        Windows Named Pipes do not support select(), so we use a short
        blocking read with exception handling instead.
        """
        if self._conn is None:
            return None

        deadline = time.monotonic() + timeout
        buf = b""

        while time.monotonic() < deadline:
            try:
                ch = self._conn.read(1)
                if not ch:
                    break
                buf += ch
                if ch == b"\n":
                    try:
                        return json.loads(buf.decode())
                    except json.JSONDecodeError:
                        buf = b""
            except OSError:
                break
            except BlockingIOError:
                time.sleep(0.01)

        return None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def send_command(self, *args) -> None:
        """Send a fire-and-forget command to mpv.

        Example:
            ipc.send_command("seek", 10, "relative")
        """
        self._send({"command": list(args)})

    def get_property(self, name: str, timeout: float = 0.5) -> object:
        """Request a property value from mpv and return it.

        Returns None if mpv does not respond in time or the property
        is unavailable.
        """
        request_id = 1
        self._send({"command": ["get_property", name], "request_id": request_id})

        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            resp = self._read_response(timeout=0.1)
            if resp is None:
                continue
            # Skip event notifications (they have no "request_id")
            if resp.get("request_id") == request_id:
                if resp.get("error") == "success":
                    return resp.get("data")
                return None

        return None

    def set_property(self, name: str, value: object) -> None:
        """Set a property on the running mpv instance.

        Example:
            ipc.set_property("pause", True)
        """
        self._send({"command": ["set_property", name, value]})
