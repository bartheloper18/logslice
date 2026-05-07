"""Persist named convert profiles (target format + optional output path)."""
from __future__ import annotations

import json
import os
from typing import Dict, Iterator, Optional

_DEFAULT_PATH = os.path.join(
    os.path.expanduser("~"), ".logslice", "convert_profiles.json"
)


def _load(store_path: str) -> dict:
    if not os.path.exists(store_path):
        return {}
    with open(store_path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _save(data: dict, store_path: str) -> None:
    os.makedirs(os.path.dirname(store_path), exist_ok=True)
    with open(store_path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)


def save_profile(
    name: str,
    target: str,
    output: Optional[str] = None,
    store_path: str = _DEFAULT_PATH,
) -> None:
    data = _load(store_path)
    data[name] = {"target": target, "output": output}
    _save(data, store_path)


def load_profile(
    name: str, store_path: str = _DEFAULT_PATH
) -> Optional[Dict]:
    return _load(store_path).get(name)


def delete_profile(name: str, store_path: str = _DEFAULT_PATH) -> bool:
    data = _load(store_path)
    if name not in data:
        return False
    del data[name]
    _save(data, store_path)
    return True


def iter_profiles(store_path: str = _DEFAULT_PATH) -> Iterator[tuple]:
    for name, cfg in _load(store_path).items():
        yield name, cfg
