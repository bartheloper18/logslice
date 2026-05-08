"""Persist and retrieve named rate-analysis profiles."""

from __future__ import annotations

import json
import os
from typing import Dict, Iterator, List, Optional

_DEFAULT_PATH = os.path.join(
    os.path.expanduser("~"), ".logslice", "rate_profiles.json"
)


def _load(path: str = _DEFAULT_PATH) -> Dict[str, dict]:
    if not os.path.exists(path):
        return {}
    with open(path, "r") as fh:
        return json.load(fh)


def _save(data: Dict[str, dict], path: str = _DEFAULT_PATH) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        json.dump(data, fh, indent=2)


def save_profile(
    name: str,
    window: int,
    label: str = "events",
    path: str = _DEFAULT_PATH,
) -> None:
    """Persist a named rate profile.

    Args:
        name: Profile identifier.
        window: Bucket window in seconds.
        label: Event noun label.
        path: Storage file path.
    """
    data = _load(path)
    data[name] = {"window": window, "label": label}
    _save(data, path)


def load_profile(
    name: str, path: str = _DEFAULT_PATH
) -> Optional[Dict[str, object]]:
    """Return a stored profile or *None* if not found."""
    return _load(path).get(name)


def delete_profile(name: str, path: str = _DEFAULT_PATH) -> bool:
    """Delete a profile.  Returns *True* if it existed."""
    data = _load(path)
    if name not in data:
        return False
    del data[name]
    _save(data, path)
    return True


def list_profiles(path: str = _DEFAULT_PATH) -> List[str]:
    """Return sorted list of stored profile names."""
    return sorted(_load(path).keys())


def iter_profiles(path: str = _DEFAULT_PATH) -> Iterator[tuple]:
    """Yield *(name, profile_dict)* pairs in alphabetical order."""
    for name, profile in sorted(_load(path).items()):
        yield name, profile
