"""Persist and recall named annotate profiles (flag presets)."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

_DEFAULT_PATH = Path.home() / ".logslice" / "annotate_profiles.json"


def _load(path: Path) -> dict:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def _save(data: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def save_profile(
    name: str,
    *,
    lineno: bool = True,
    elapsed: bool = False,
    delta: bool = False,
    path: Optional[Path] = None,
) -> None:
    """Save an annotate flag preset under *name*."""
    store_path = Path(path) if path else _DEFAULT_PATH
    data = _load(store_path)
    data[name] = {"lineno": lineno, "elapsed": elapsed, "delta": delta}
    _save(data, store_path)


def load_profile(name: str, *, path: Optional[Path] = None) -> Optional[dict]:
    """Return the stored profile dict for *name*, or None if not found."""
    store_path = Path(path) if path else _DEFAULT_PATH
    return _load(store_path).get(name)


def delete_profile(name: str, *, path: Optional[Path] = None) -> bool:
    """Delete profile *name*. Returns True if it existed."""
    store_path = Path(path) if path else _DEFAULT_PATH
    data = _load(store_path)
    if name not in data:
        return False
    del data[name]
    _save(data, store_path)
    return True


def list_profiles(*, path: Optional[Path] = None) -> list[str]:
    """Return sorted list of saved profile names."""
    store_path = Path(path) if path else _DEFAULT_PATH
    return sorted(_load(store_path).keys())
