"""Globala användarinställningar — hushållsstorlek m.m."""

from pathlib import Path

import yaml

DATA_DIR      = Path(__file__).parent.parent / "data"
SETTINGS_PATH = DATA_DIR / "settings.yaml"

_DEFAULTS = {
    "household_size": 4,
}


def load() -> dict:
    if not SETTINGS_PATH.exists():
        save(_DEFAULTS.copy())
        return _DEFAULTS.copy()
    with open(SETTINGS_PATH, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return {**_DEFAULTS, **data}


def save(settings: dict) -> None:
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        yaml.dump(settings, f, allow_unicode=True, sort_keys=False)


def get(key: str):
    return load().get(key, _DEFAULTS.get(key))


def set_value(key: str, value) -> None:
    settings = load()
    settings[key] = value
    save(settings)
