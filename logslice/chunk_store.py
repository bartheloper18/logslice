"""Persist named chunk profiles (size/seconds + prefix) to disk."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, List, Optional

_DEFAULT_PATH = Path.home() / ".logslice" / "chunk_profiles.json"


def _load(path: Path) -> Dict[str, dict]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def _save(data: Dict[str, dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def save_profile(name: str, profile: dict, path: Path = _DEFAULT_PATH) -> None:
    """Persist *profile* under *name*."""
    data = _load(path)
    data[name] = profile
    _save(data, path)


def load_profile(name: str, path: Path = _DEFAULT_PATH) -> Optional[dict]:
    """Return profile dict for *name*, or ``None`` if not found."""
    return _load(path).get(name)


def delete_profile(name: str, path: Path = _DEFAULT_PATH) -> bool:
    """Remove *name*. Returns True if it existed."""
    data = _load(path)
    if name not in data:
        return False
    del data[name]
    _save(data, path)
    return True


def list_profiles(path: Path = _DEFAULT_PATH) -> List[str]:
    """Return sorted list of stored profile names."""
    return sorted(_load(path).keys())


def rename_profile(
    old_name: str, new_name: str, path: Path = _DEFAULT_PATH
) -> bool:
    """Rename an existing profile from *old_name* to *new_name*.

    Returns ``True`` if the rename succeeded, or ``False`` if *old_name* was
    not found.  Raises ``ValueError`` if *new_name* already exists.
    """
    data = _load(path)
    if old_name not in data:
        return False
    if new_name in data:
        raise ValueError(f"Profile {new_name!r} already exists.")
    data[new_name] = data.pop(old_name)
    _save(data, path)
    return True
