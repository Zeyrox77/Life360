"""Life360 Desktop application.

Runs the dashboard as a standalone native window (no browser required). It
starts the FastAPI backend on a local port in a background thread and then
opens a native webview window pointing at it.

The same backend powers the browser variant, so all the Life360 logic
(Cloudflare bypass, token validation, data endpoints) is shared.

Run from source:
    python desktop.py

Build a Windows .exe:
    see Life360.spec / build_windows.bat / the GitHub release workflow.
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

# A fixed port keeps the web origin (scheme://host:port) stable across launches.
# Browser localStorage - where the access token is saved - is scoped to the
# origin, so a stable port is what keeps you signed in after closing the app.
PREFERRED_PORT = 17360


def _resolve_port() -> int:
    """Use a fixed port when possible; fall back to a random free one.

    The fixed port is important: it keeps localStorage (and therefore the saved
    login token) available between app restarts.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.bind((HOST, PREFERRED_PORT))
            return PREFERRED_PORT
        except OSError:
            sock.bind((HOST, 0))
            return sock.getsockname()[1]


def _storage_path() -> str:
    """Per-user directory where the webview keeps localStorage/cookies.

    Keeping persistent storage here means the access token entered in the app
    survives restarts (until Life360 expires it).
    """
    if sys.platform.startswith("win"):
        base = Path.home() / "AppData" / "Local" / "Life360Dashboard"
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support" / "Life360Dashboard"
    else:
        base = Path.home() / ".local" / "share" / "life360-dashboard"
    base.mkdir(parents=True, exist_ok=True)
    return str(base)


def _run_server(port: int) -> None:
    """Run the FastAPI backend (blocking); intended for a daemon thread."""
    config = uvicorn.Config(fastapi_app, host=HOST, port=port, log_level="warning")
    server = uvicorn.Server(config)
    server.run()


def _wait_until_ready(port: int, timeout: float = 30.0) -> bool:
    """Poll the health endpoint until the server responds or we time out."""
    url = f"http://{HOST}:{port}/api/health"
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=1) as resp:
                if resp.status == 200:
                    return True
        except Exception:
            time.sleep(0.2)
    return False


def main() -> None:
    port = _resolve_port()

    server_thread = threading.Thread(target=_run_server, args=(port,), daemon=True)
    server_thread.start()

    if not _wait_until_ready(port):
        print("Error: the Life360 backend did not start in time.", file=sys.stderr)
        sys.exit(1)

    webview.create_window(
        WINDOW_TITLE,
        f"http://{HOST}:{port}/",
        width=1280,
        height=820,
        min_size=(960, 600),
    )
    # private_mode=False -> persistent localStorage so the token is remembered.
    webview.start(private_mode=False, storage_path=_storage_path())


if __name__ == "__main__":
    main()
