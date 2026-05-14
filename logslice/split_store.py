"""Persist and recall named split profiles."""

from __future__ import annotations

import json
import os
from typing import Dict, List, Optional

_DEFAULT_PATH = os.path.join(os.path.expanduser("~"), ".logslice", "split_profiles.json")


def _load(path: str = _DEFAULT_PATH) -> Dict[str, dict]:
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _save(data: Dict[str, dict], path: str = _DEFAULT_PATH) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)


def save_profile(name: str, profile: dict, path: str = _DEFAULT_PATH) -> None:
    """Persist a named split *profile*."""
    data = _load(path)
    data[name] = profile
    _save(data, path)


def load_profile(name: str, path: str = _DEFAULT_PATH) -> Optional[dict]:
    """Return a previously saved profile, or *None* if not found."""
    return _load(path).get(name)


def delete_profile(name: str, path: str = _DEFAULT_PATH) -> bool:
    """Delete a profile; returns *True* when it existed."""
    data = _load(path)
    if name not in data:
        return False
    del data[name]
    _save(data, path)
    return True


def list_profiles(path: str = _DEFAULT_PATH) -> List[str]:
    """Return all stored profile names in sorted order."""
    return sorted(_load(path).keys())
