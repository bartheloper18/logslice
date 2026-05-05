"""Tail support: follow a log file for new lines (like tail -f)."""

import time
import os
from typing import Callable, Optional


DEFAULT_POLL_INTERVAL = 0.2  # seconds


def read_last_lines(path: str, n: int = 10) -> list[str]:
    """Return the last *n* lines of *path* without reading the whole file."""
    if n <= 0:
        return []
    with open(path, "rb") as fh:
        # Seek from end, reading chunks until we have n newlines
        chunk_size = 1024
        fh.seek(0, 2)
        file_size = fh.tell()
        buf = b""
        pos = file_size
        while pos > 0 and buf.count(b"\n") < n + 1:
            read_size = min(chunk_size, pos)
            pos -= read_size
            fh.seek(pos)
            buf = fh.read(read_size) + buf
        lines = buf.decode(errors="replace").splitlines(keepends=True)
        return lines[-n:] if len(lines) >= n else lines


def follow_file(
    path: str,
    callback: Callable[[str], None],
    poll_interval: float = DEFAULT_POLL_INTERVAL,
    stop_after: Optional[int] = None,
) -> None:
    """Continuously read new lines appended to *path* and pass each to *callback*.

    Parameters
    ----------
    path:          Path to the log file.
    callback:      Called with each new line (including newline character).
    poll_interval: Seconds between polls when no new data is available.
    stop_after:    If set, stop after emitting this many lines (useful for tests).
    """
    emitted = 0
    with open(path, "r", errors="replace") as fh:
        fh.seek(0, 2)  # jump to end
        while True:
            line = fh.readline()
            if line:
                callback(line)
                emitted += 1
                if stop_after is not None and emitted >= stop_after:
                    return
            else:
                # Check if file was rotated (inode changed or file shrank)
                try:
                    st = os.stat(path)
                    if st.st_size < fh.tell():
                        fh.seek(0)  # file was truncated / rotated
                except FileNotFoundError:
                    return
                time.sleep(poll_interval)
