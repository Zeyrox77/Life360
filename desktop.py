"""Life360 Desktop application.

Runs the dashboard as a standalone native window (no browser required): it
starts the local backend in a background thread and shows it in a webview window.

Run from source:
    python desktop.py
"""

from __future__ import annotations

import socket
import sys
import threading
import time
import urllib.request
from pathlib import Path

import uvicorn
import webview

from backend.main import app as fastapi_app

HOST = "127.0.0.1"
WINDOW_TITLE = "Life360 Desktop"

# A FIXED port is essential: the saved login token lives in the webview's
# localStorage, which is scoped to the origin (scheme://host:port). If the port
# changed between launches, the token would appear to vanish and you'd be logged
# out. Using the same port every time keeps the origin - and the login - stable.
PORT = 17360


def _backend_is_running() -> bool:
    """Return True if our backend is already serving on the fixed port."""
    try:
        with urllib.request.urlopen(f"http://{HOST}:{PORT}/api/health", timeout=1) as resp:
            return resp.status == 200
    except Exception:
        return False


def _make_listen_socket() -> socket.socket | None:
    """Bind a listening socket on the fixed port, or return None if unavailable.

    SO_REUSEADDR lets us re-bind immediately after a previous instance closed,
    even while the port is still in the OS "TIME_WAIT" state - which is exactly
    what previously forced a fallback to a random port (and logged the user out).
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.bind((HOST, PORT))
    except OSError:
        sock.close()
        return None
    sock.listen(128)
    return sock


def _storage_path() -> str:
    """Per-user directory where the webview keeps localStorage/cookies.

    Persistent storage here is what remembers the access token between launches.
    """
    if sys.platform.startswith("win"):
        base = Path.home() / "AppData" / "Local" / "Life360Dashboard"
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support" / "Life360Dashboard"
    else:
        base = Path.home() / ".local" / "share" / "life360-dashboard"
    base.mkdir(parents=True, exist_ok=True)
    return str(base)


def _run_server(sock: socket.socket) -> None:
    """Run the FastAPI backend on the given socket (intended for a daemon thread)."""
    config = uvicorn.Config(fastapi_app, log_level="warning")
    server = uvicorn.Server(config)
    server.run(sockets=[sock])


def _wait_until_ready(timeout: float = 30.0) -> bool:
    """Poll the health endpoint until the server responds or we time out."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        if _backend_is_running():
            return True
        time.sleep(0.2)
    return False


def main() -> None:
    # Reuse an already-running instance on the fixed port if present; otherwise
    # start our own server. Either way the window always points at the same
    # origin (http://127.0.0.1:17360), so the saved login persists.
    if not _backend_is_running():
        sock = _make_listen_socket()
        if sock is None:
            print(
                f"Error: port {PORT} is in use by another application. "
                "Close it and try again.",
                file=sys.stderr,
            )
            sys.exit(1)
        threading.Thread(target=_run_server, args=(sock,), daemon=True).start()
        if not _wait_until_ready():
            print("Error: the Life360 backend did not start in time.", file=sys.stderr)
            sys.exit(1)

    webview.create_window(
        WINDOW_TITLE,
        f"http://{HOST}:{PORT}/",
        width=1280,
        height=820,
        min_size=(960, 600),
    )
    # private_mode=False -> persistent localStorage so the token is remembered.
    webview.start(private_mode=False, storage_path=_storage_path())


if __name__ == "__main__":
    main()
