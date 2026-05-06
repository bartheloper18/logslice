"""Persist and load named redaction profiles (sets of patterns)."""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional

DEFAULT_STORE = Path.home() / ".logslice" / "redact_profiles.json"


def _load(store_path: Path) -> Dict[str, dict]:
    if store_path.exists():
        with open(store_path) as fh:
            return json.load(fh)
    return {}


def _save(data: Dict[str, dict], store_path: Path) -> None:
    store_path.parent.mkdir(parents=True, exist_ok=True)
    with open(store_path, "w") as fh:
        json.dump(data, fh, indent=2)


def save_profile(
    name: str,
    patterns: List[str],
    builtins: Optional[List[str]] = None,
    mask: str = "[REDACTED]",
    store_path: Path = DEFAULT_STORE,
) -> None:
    """Persist a named redaction profile."""
    data = _load(store_path)
    data[name] = {"patterns": patterns, "builtins": builtins or [], "mask": mask}
    _save(data, store_path)


def load_profile(
    name: str,
    store_path: Path = DEFAULT_STORE,
) -> Optional[dict]:
    """Return the profile dict for *name*, or None if not found."""
    return _load(store_path).get(name)


def delete_profile(
    name: str,
    store_path: Path = DEFAULT_STORE,
) -> bool:
    """Remove a profile by name. Returns True if it existed."""
    data = _load(store_path)
    if name in data:
        del data[name]
        _save(data, store_path)
        return True
    return False


def list_profiles(store_path: Path = DEFAULT_STORE) -> List[str]:
    """Return sorted list of profile names."""
    return sorted(_load(store_path).keys())
