"""Butiksprofiler — hanterar sparade layout-profiler för handlingslistan."""

import re
from pathlib import Path

import yaml

DATA_DIR = Path(__file__).parent.parent / "data"
ORDER_PATH = DATA_DIR / "shopping_order.yaml"

DEFAULT_CATEGORY_ORDER = [
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

_DEFAULT_DATA = {
    "active_profile": "standard",
    "profiles": {
        "standard": {
            "name": "Standard",
            "category_order": DEFAULT_CATEGORY_ORDER[:],
            "item_overrides": {},
        }
    },
}


def load() -> dict:
    """Ladda shopping_order.yaml. Skapar standardfil om den saknas."""
    if not ORDER_PATH.exists():
        save(_DEFAULT_DATA)
        return _DEFAULT_DATA
    with open(ORDER_PATH, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    # Säkerställ att aktiv profil finns
    if data.get("active_profile") not in data.get("profiles", {}):
        data["active_profile"] = next(iter(data.get("profiles", {_DEFAULT_DATA["active_profile"]: _DEFAULT_DATA["profiles"]["standard"]})))
    return data


def save(data: dict) -> None:
    """Skriv data till shopping_order.yaml."""
    with open(ORDER_PATH, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False, default_flow_style=False)


def all_profiles() -> dict:
    """Returnera {profile_id: profile_dict} för alla profiler."""
    return load().get("profiles", {})


def active_id() -> str:
    """Returnera ID för aktiv profil."""
    return load().get("active_profile", "standard")


def active() -> dict:
    """Returnera den aktiva profilens dict."""
    data = load()
    pid = data.get("active_profile", "standard")
    return data["profiles"][pid]


def set_active(profile_id: str) -> None:
    """Sätt aktiv profil."""
    data = load()
    if profile_id not in data.get("profiles", {}):
        raise ValueError(f"Profil '{profile_id}' finns inte.")
    data["active_profile"] = profile_id
    save(data)


def _slugify(name: str) -> str:
    """Skapa ett snake_case ID från ett namn."""
    slug = name.lower().strip()
    slug = re.sub(r"[åä]", "a", slug)
    slug = re.sub(r"[ö]", "o", slug)
    slug = re.sub(r"[^a-z0-9]+", "_", slug)
    slug = slug.strip("_")
    return slug or "profil"


def create(name: str) -> str:
    """Skapa ny profil som kopia av aktiv profil. Returnerar nytt profile_id."""
    data = load()
    base_slug = _slugify(name)
    # Garantera unikt ID
    slug = base_slug
    counter = 2
    while slug in data.get("profiles", {}):
        slug = f"{base_slug}_{counter}"
        counter += 1

    active_profile = data["profiles"].get(data["active_profile"], {})
    data["profiles"][slug] = {
        "name": name,
        "category_order": list(active_profile.get("category_order", DEFAULT_CATEGORY_ORDER)),
        "item_overrides": dict(active_profile.get("item_overrides", {})),
    }
    save(data)
    return slug


def delete(profile_id: str) -> None:
    """Ta bort profil. Vägrar om det bara finns en profil."""
    data = load()
    profiles = data.get("profiles", {})
    if len(profiles) <= 1:
        raise ValueError("Kan inte ta bort den enda profilen.")
    if profile_id not in profiles:
        raise ValueError(f"Profil '{profile_id}' finns inte.")
    del profiles[profile_id]
    # Om aktiv profil togs bort, välj den första återstående
    if data.get("active_profile") == profile_id:
        data["active_profile"] = next(iter(profiles))
    data["profiles"] = profiles
    save(data)


def rename(profile_id: str, new_name: str) -> None:
    """Byt namn på profil."""
    data = load()
    if profile_id not in data.get("profiles", {}):
        raise ValueError(f"Profil '{profile_id}' finns inte.")
    data["profiles"][profile_id]["name"] = new_name
    save(data)


def save_layout(
    profile_id: str,
    category_order: list,
    item_overrides: dict,
) -> None:
    """Spara kategoriordning och item-overrides för en profil."""
    data = load()
    if profile_id not in data.get("profiles", {}):
        raise ValueError(f"Profil '{profile_id}' finns inte.")
    data["profiles"][profile_id]["category_order"] = list(category_order)
    data["profiles"][profile_id]["item_overrides"] = dict(item_overrides)
    save(data)
