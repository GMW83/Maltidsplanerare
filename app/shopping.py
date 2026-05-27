"""Handlingslista-logik — bygg och gruppera inköpslista från veckoplan."""

from pathlib import Path

import yaml

DATA_DIR = Path(__file__).parent.parent / "data"

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
    "ovrigt",
]

CATEGORY_NAMES = {
    "frukt_och_gront": "Frukt och grönt",
    "kott_och_chark": "Kött och chark",
    "mejeri_och_agg": "Mejeri och ägg",
    "torrvaror": "Torrvaror",
    "konserver": "Konserver",
    "frysta_varor": "Frysta varor",
    "brod_och_bakverk": "Bröd och bakverk",
    "drycker": "Drycker",
    "kryddor_och_smaksattare": "Kryddor och smaksättare",
    "ovrigt": "Övrigt",
}


def _load_items() -> dict:
    with open(DATA_DIR / "items.yaml", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return {item["id"]: item for item in data.get("items", [])}


def _load_recipe(recipe_id: str) -> dict | None:
    path = DATA_DIR / "recipes" / f"{recipe_id}.yaml"
    if not path.exists():
        return None
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def build_shopping_list(weekly_plan: dict) -> list[dict]:
    """
    Returnerar handlingslista sorterad efter butiksordning.
    Varje post: {"category_id", "category_name", "items": [...]}
    Varje vara: {"id", "name_sv", "amount", "unit"}
    Aggregerar mängder om samma vara ingår i flera recept.
    Inkluderar bara varor med role='ingredient'.
    """
    items_db = _load_items()
    aggregated: dict[str, dict] = {}

    for meal in weekly_plan.get("meals", []):
        recipe = _load_recipe(meal["recipe_id"])
        if not recipe:
            continue
        for ing in recipe.get("ingredients", []):
            iid = ing["ingredient_id"]
            item = items_db.get(iid)
            if not item or item.get("role") != "ingredient":
                continue
            if iid not in aggregated:
                aggregated[iid] = {
                    "id": iid,
                    "name_sv": item["name_sv"],
                    "category": item.get("category", "ovrigt"),
                    "amount": 0,
                    "unit": ing["unit"],
                }
            aggregated[iid]["amount"] += ing["amount"]

    by_category: dict[str, list] = {}
    for item_data in aggregated.values():
        cat = item_data["category"]
        by_category.setdefault(cat, []).append(item_data)

    for cat in by_category:
        by_category[cat].sort(key=lambda x: x["name_sv"])

    return [
        {
            "category_id": cat_id,
            "category_name": CATEGORY_NAMES.get(cat_id, cat_id),
            "items": by_category[cat_id],
        }
        for cat_id in CATEGORY_ORDER
        if cat_id in by_category
    ]
