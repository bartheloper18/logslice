"""Persistence for saved field-filter profiles."""

import json
import os
from typing import Dict, Iterator, List, Optional

_DEFAULT_PATH = os.path.join(
    os.path.expanduser("~"), ".logslice", "field_profiles.json"
)


def _load(path: str = _DEFAULT_PATH) -> Dict[str, dict]:
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _save(data: Dict[str, dict], path: str = _DEFAULT_PATH) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)


def save_profile(
    name: str,
    field: str,
    value: Optional[str] = None,
    ignore_case: bool = False,
    path: str = _DEFAULT_PATH,
) -> None:
    """Persist a named field-filter profile."""
    data = _load(path)
    data[name] = {"field": field, "value": value, "ignore_case": ignore_case}
    _save(data, path)


def load_profile(name: str, path: str = _DEFAULT_PATH) -> Optional[dict]:
    """Return profile dict for *name* or None if not found."""
    return _load(path).get(name)


def delete_profile(name: str, path: str = _DEFAULT_PATH) -> bool:
    """Remove *name*; return True if it existed."""
    data = _load(path)
    if name not in data:
        return False
    del data[name]
    _save(data, path)
    return True


def iter_profiles(path: str = _DEFAULT_PATH) -> Iterator[str]:
    """Yield all saved profile names."""
    yield from _load(path).keys()


def list_profiles(path: str = _DEFAULT_PATH) -> List[str]:
    """Return sorted list of saved profile names."""
    return sorted(iter_profiles(path))
