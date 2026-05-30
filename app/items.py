"""Varuhantering — lägg till och ta bort varor i items.yaml."""

import re
import unicodedata
from pathlib import Path

import yaml

DATA_DIR   = Path(__file__).parent.parent / "data"
ITEMS_PATH = DATA_DIR / "items.yaml"
RECIPES_DIR = DATA_DIR / "recipes"


def _to_id(name: str) -> str:
    nfd = unicodedata.normalize("NFD", name.lower().strip())
    ascii_n = "".join(c for c in nfd if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", "_", ascii_n).strip("_")


def _load_raw() -> dict:
    with open(ITEMS_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f) or {"items": []}


def _save_raw(data: dict) -> None:
    with open(ITEMS_PATH, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False)


def name_exists(name_sv: str) -> bool:
    data = _load_raw()
    return any(item["name_sv"].lower() == name_sv.lower().strip() for item in data.get("items", []))


def generate_id(name: str) -> str:
    """Returnera ett ledigt snake_case-ID baserat på namnet."""
    base = _to_id(name)
    if not base:
        base = "vara"
    data = _load_raw()
    existing = {item["id"] for item in data.get("items", [])}
    if base not in existing:
        return base
    i = 2
    while f"{base}_{i}" in existing:
        i += 1
    return f"{base}_{i}"


def id_exists(item_id: str) -> bool:
    data = _load_raw()
    return any(item["id"] == item_id for item in data.get("items", []))


def add_item(
    name_sv: str,
    category: str,
    unit: str,
    role: str,
    synonyms: list[str] | None = None,
) -> str:
    """Lägg till vara i items.yaml. Returnerar det tilldelade ID:t."""
    item_id = generate_id(name_sv)
    entry: dict = {
        "id":       item_id,
        "name_sv":  name_sv.strip(),
        "category": category,
        "unit":     unit,
        "role":     role,
    }
    if synonyms:
        entry["synonyms"] = [s.strip() for s in synonyms if s.strip()]
    data = _load_raw()
    data.setdefault("items", []).append(entry)
    _save_raw(data)
    return item_id


def find_recipe_uses(item_id: str) -> list[str]:
    """Returnera lista med recepttitlar som använder item_id som ingrediens."""
    titles = []
    for path in sorted(RECIPES_DIR.glob("*.yaml")):
        with open(path, encoding="utf-8") as f:
            recipe = yaml.safe_load(f) or {}
        for ing in recipe.get("ingredients", []):
            if ing.get("ingredient_id") == item_id:
                titles.append(recipe.get("title", path.stem))
                break
    return titles


def delete_item(item_id: str) -> None:
    """Ta bort vara från items.yaml. Anroparen ansvarar för att kontrollera receptanvändning."""
    data = _load_raw()
    data["items"] = [item for item in data.get("items", []) if item["id"] != item_id]
    _save_raw(data)
