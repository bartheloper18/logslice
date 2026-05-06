"""Persist named sampling profiles (every / fraction / seed) to disk."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterator

_DEFAULT_STORE = Path.home() / ".logslice" / "sample_profiles.json"


def _load(store: Path) -> dict:
    if store.exists():
        return json.loads(store.read_text())
    return {}


def _save(data: dict, store: Path) -> None:
    store.parent.mkdir(parents=True, exist_ok=True)
    store.write_text(json.dumps(data, indent=2))


def save_profile(
    name: str,
    *,
    every: int = 0,
    fraction: float = 0.0,
    seed: int | None = None,
    store: Path = _DEFAULT_STORE,
) -> None:
    """Persist a named sampling profile."""
    if not every and not fraction:
        raise ValueError("Profile must specify 'every' or 'fraction'.")
    data = _load(store)
    data[name] = {"every": every, "fraction": fraction, "seed": seed}
    _save(data, store)


def load_profile(name: str, *, store: Path = _DEFAULT_STORE) -> dict | None:
    """Return the profile dict or *None* if not found."""
    return _load(store).get(name)


def delete_profile(name: str, *, store: Path = _DEFAULT_STORE) -> bool:
    """Delete a profile.  Returns *True* if it existed."""
    data = _load(store)
    if name in data:
        del data[name]
        _save(data, store)
        return True
    return False


def iter_profiles(*, store: Path = _DEFAULT_STORE) -> Iterator[tuple[str, dict]]:
    """Yield ``(name, profile_dict)`` pairs for every saved profile."""
    yield from _load(store).items()
