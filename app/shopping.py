"""Handlingslista — fullständig lista med persistent tillstånd."""

from datetime import date
from pathlib import Path

import yaml

from app.planner import current_week_start

# ── Enhetskonvertering ────────────────────────────────────────────────────────

_UNIT_BASE: dict[str, tuple[str, float]] = {
    "g":   ("g",  1),
    "kg":  ("g",  1000),
    "ml":  ("ml", 1),
    "cl":  ("ml", 10),
    "dl":  ("ml", 100),
    "l":   ("ml", 1000),
    "st":  ("st", 1),
    "msk": ("msk", 1),
    "tsk": ("tsk", 1),
    "krm": ("krm", 1),
}


def _normalize_unit(amount: float, unit: str) -> tuple[float, str]:
    base_unit, factor = _UNIT_BASE.get(unit.lower().strip(), (unit, 1))
    return amount * factor, base_unit


def format_quantity(amount: float, unit: str) -> str:
    """Formatera mängd för visning i handlingslistan."""
    u = unit.lower().strip()
    if u == "g":
        if amount >= 1000:
            return f"{amount / 1000:g} kg"
        return f"{round(amount)} g"
    if u == "ml":
        if amount >= 1000:
            return f"{amount / 1000:g} L"
        if amount >= 100:
            return f"{amount / 100:g} dl"
        return f"{round(amount)} ml"
    if u == "st":
        return f"{round(amount)} st"
    n = int(amount) if amount == int(amount) else round(amount, 1)
    return f"{n} {unit}"

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
        return {"checked": [], "extras": [], "quantities_by_week": {}}
    with open(STATE_PATH, encoding="utf-8") as f:
        state = yaml.safe_load(f) or {}
    return {
        "checked":            list(state.get("checked")            or []),
        "extras":             list(state.get("extras")             or []),
        "quantities_by_week": dict(state.get("quantities_by_week") or {}),
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

def apply_meal_plan(plan: dict, household_size: int = 4, week_start: date = None) -> list[str]:
    """Bocka i ingredienser från godkänd meny och beräkna inköpsmängder.

    Mängderna lagras i en hink per vecka (quantities_by_week), så att flera
    veckors planer kan bidra till listan samtidigt utan att skriva över varandra.
    Returnerar lista med läsbara namn på ingredienser som saknas i varudatabasen
    och därför lagts till automatiskt under 'Extra denna vecka'.
    """
    state = load_state()
    checked_set = set(state["checked"])
    quantities: dict[str, dict] = {}   # denna veckas hink, räknas om från noll
    unmatched_qty: dict[str, dict] = {}  # ingredient_id → {amount, unit} för ej matchade
    items_db = load_items()

    for meal in plan.get("meals", []):
        recipe = _load_recipe(meal["recipe_id"])
        if not recipe:
            continue
        recipe_servings = max(1, recipe.get("servings", 4))
        scale = household_size / recipe_servings

        for ing in recipe.get("ingredients", []):
            item_id = ing["ingredient_id"]
            item = items_db.get(item_id)

            if item is None:
                # Inte i varudatabasen — samla skalad mängd för extras
                if item_id not in unmatched_qty:
                    # Spara display_name (med å/ä/ö) om det finns, annars fallback på ID
                    display = ing.get("display_name") or item_id.replace("_", " ")
                    unmatched_qty[item_id] = {"display_name": display}
                raw_amount = ing.get("amount")
                raw_unit = ing.get("unit", "")
                if raw_amount is not None and raw_unit:
                    norm_amount, norm_unit = _normalize_unit(raw_amount * scale, raw_unit)
                    existing = unmatched_qty[item_id]
                    if existing.get("unit") == norm_unit:
                        existing["amount"] = existing.get("amount", 0) + norm_amount
                    else:
                        existing["amount"] = norm_amount
                        existing["unit"] = norm_unit
                continue

            if not (item.get("role") in INCLUDED_ROLES):
                continue
            checked_set.add(item_id)

            raw_amount = ing.get("amount")
            raw_unit   = ing.get("unit", "")
            if raw_amount is not None and raw_unit:
                norm_amount, norm_unit = _normalize_unit(raw_amount * scale, raw_unit)
                if item_id in quantities and quantities[item_id]["unit"] == norm_unit:
                    quantities[item_id]["amount"] += norm_amount
                else:
                    quantities[item_id] = {"amount": norm_amount, "unit": norm_unit}

    # Lägg till omatchade i extras (dedup på namn, summerade mängder)
    extras = state.get("extras", [])
    existing_names = {e["text"].split(" — ")[0].lower() for e in extras}
    added_names: list[str] = []
    for item_id, qty in unmatched_qty.items():
        name = qty.get("display_name") or item_id.replace("_", " ")
        if name.lower() in existing_names:
            continue
        if qty.get("amount") and qty.get("unit"):
            text = f"{name} — {format_quantity(qty['amount'], qty['unit'])}"
        else:
            text = name
        extras.append({"text": text, "checked": True})
        existing_names.add(name.lower())
        added_names.append(name)

    week_key = (week_start or current_week_start()).isoformat()
    qbw = state.get("quantities_by_week", {})
    qbw[week_key] = quantities
    cws = current_week_start()
    for k in [k for k in qbw if date.fromisoformat(k) < cws]:
        del qbw[k]

    state["checked"]            = list(checked_set)
    state["quantities_by_week"] = qbw
    state["extras"]             = extras
    save_state(state)
    return added_names


def _flatten_quantities(qbw: dict) -> dict:
    """Summera alla veckors hinkar till en total per item_id, för visning."""
    total: dict[str, dict] = {}
    for bucket in qbw.values():
        for item_id, qty in bucket.items():
            if item_id in total and total[item_id]["unit"] == qty["unit"]:
                total[item_id]["amount"] += qty["amount"]
            else:
                total[item_id] = dict(qty)
    return total


# ── Fullständig lista ─────────────────────────────────────────────────────────

def get_full_list(profile: dict = None) -> list[dict]:
    """Returnera alla varor grupperade per kategori med bockningsstatus.

    Om profile är angiven används profilens category_order och item_overrides.
    """
    items_db = load_items()
    state = load_state()
    checked_set = set(state["checked"])

    # Bestäm kategoriordning och overrides från profil eller standardvärden
    if profile is not None:
        cat_order = profile.get("category_order", CATEGORY_ORDER)
        item_overrides = profile.get("item_overrides", {})
        category_names_override = profile.get("category_names", {})
    else:
        cat_order = CATEGORY_ORDER
        item_overrides = {}
        category_names_override = {}

    quantities = _flatten_quantities(state.get("quantities_by_week", {}))

    by_category: dict[str, list] = {}
    for item_id, item in items_db.items():
        if item.get("role") not in INCLUDED_ROLES:
            continue
        # Använd override-kategori om den finns, annars items.yaml-kategorin
        cat = item_overrides.get(item_id) or item.get("category", "ovrigt")
        by_category.setdefault(cat, []).append({
            "id":       item_id,
            "name_sv":  item["name_sv"],
            "role":     item.get("role"),
            "checked":  item_id in checked_set,
            "quantity": quantities.get(item_id),
        })

    for cat in by_category:
        by_category[cat].sort(key=lambda x: x["name_sv"])

    return [
        {
            "category_id":   cat_id,
            "category_name": category_names_override.get(cat_id) or CATEGORY_NAMES.get(cat_id, cat_id),
            "items":         by_category[cat_id],
        }
        for cat_id in cat_order
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


def clear_quantities_for_unchecked() -> None:
    """Ta bort mängder för alla urcheckade varor. Ibockade varors mängder bevaras."""
    state = load_state()
    checked_set = set(state["checked"])
    qbw = state.get("quantities_by_week", {})
    state["quantities_by_week"] = {
        wk: {k: v for k, v in bucket.items() if k in checked_set}
        for wk, bucket in qbw.items()
    }
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
