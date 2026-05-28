"""Handlingslista — fullständig lista med persistent tillstånd."""

from pathlib import Path

import yaml

DATA_DIR = Path(__file__).parent.parent / "data"
STATE_PATH = DATA_DIR / "shopping_state.yaml"

CATEGORY_ORDER = [
    "frukt_och_gront",
    "kott_och_chark",
    "mejeri_och_agg",
    "torrvaror",
    "konserver",
    "frysta_varor",
    "brod_och_bakverk",
    "drycker",
    "kryddor_och_smaksattare",
    "hushall",
    "ovrigt",
]

CATEGORY_NAMES = {
    "frukt_och_gront":        "Frukt och grönt",
    "kott_och_chark":         "Kött och chark",
    "mejeri_och_agg":         "Mejeri och ägg",
    "torrvaror":              "Torrvaror",
    "konserver":              "Konserver",
    "frysta_varor":           "Frysta varor",
    "brod_och_bakverk":       "Bröd och bakverk",
    "drycker":                "Drycker",
    "kryddor_och_smaksattare":"Kryddor och smaksättare",
    "hushall":                "Hushåll och övrigt",
    "ovrigt":                 "Övrigt",
}

INCLUDED_ROLES = {"ingredient", "pantry_staple", "regular_purchase"}


# ── State I/O ────────────────────────────────────────────────────────────────

def load_state() -> dict:
    if not STATE_PATH.exists():
        return {"checked": [], "extras": []}
    with open(STATE_PATH, encoding="utf-8") as f:
        state = yaml.safe_load(f) or {}
    return {
        "checked": list(state.get("checked") or []),
        "extras":  list(state.get("extras")  or []),
    }


def save_state(state: dict) -> None:
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        yaml.dump(state, f, allow_unicode=True, sort_keys=False)


# ── Items ─────────────────────────────────────────────────────────────────────

def load_items() -> dict:
    with open(DATA_DIR / "items.yaml", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return {item["id"]: item for item in data.get("items", [])}


def _load_recipe(recipe_id: str) -> dict | None:
    path = DATA_DIR / "recipes" / f"{recipe_id}.yaml"
    if not path.exists():
        return None
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


# ── Menyplanering → handlingslista ───────────────────────────────────────────

def apply_meal_plan(plan: dict) -> None:
    """Bocka i ingredienser från godkänd meny. Befintliga bockar rörs inte."""
    state = load_state()
    checked_set = set(state["checked"])
    items_db = load_items()

    for meal in plan.get("meals", []):
        recipe = _load_recipe(meal["recipe_id"])
        if not recipe:
            continue
        for ing in recipe.get("ingredients", []):
            item = items_db.get(ing["ingredient_id"])
            if item and item.get("role") == "ingredient":
                checked_set.add(ing["ingredient_id"])

    state["checked"] = list(checked_set)
    save_state(state)


# ── Fullständig lista ─────────────────────────────────────────────────────────

def get_full_list() -> list[dict]:
    """Returnera alla varor grupperade per kategori med bockningsstatus."""
    items_db = load_items()
    state = load_state()
    checked_set = set(state["checked"])

    by_category: dict[str, list] = {}
    for item_id, item in items_db.items():
        if item.get("role") not in INCLUDED_ROLES:
            continue
        cat = item.get("category", "ovrigt")
        by_category.setdefault(cat, []).append({
            "id":      item_id,
            "name_sv": item["name_sv"],
            "role":    item.get("role"),
            "checked": item_id in checked_set,
        })

    for cat in by_category:
        by_category[cat].sort(key=lambda x: x["name_sv"])

    return [
        {
            "category_id":   cat_id,
            "category_name": CATEGORY_NAMES.get(cat_id, cat_id),
            "items":         by_category[cat_id],
        }
        for cat_id in CATEGORY_ORDER
        if cat_id in by_category
    ]


# ── Bocka ─────────────────────────────────────────────────────────────────────

def set_item_checked(item_id: str, checked: bool) -> None:
    state = load_state()
    checked_set = set(state["checked"])
    if checked:
        checked_set.add(item_id)
    else:
        checked_set.discard(item_id)
    state["checked"] = list(checked_set)
    save_state(state)


# ── Extraposter ───────────────────────────────────────────────────────────────

def add_extra(text: str) -> None:
    state = load_state()
    state.setdefault("extras", []).append({"text": text.strip(), "checked": True})
    save_state(state)


def set_extra_checked(idx: int, checked: bool) -> None:
    state = load_state()
    extras = state.get("extras", [])
    if 0 <= idx < len(extras):
        extras[idx]["checked"] = checked
    state["extras"] = extras
    save_state(state)


def remove_extra(idx: int) -> None:
    state = load_state()
    extras = state.get("extras", [])
    if 0 <= idx < len(extras):
        extras.pop(idx)
    state["extras"] = extras
    save_state(state)
