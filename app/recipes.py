"""Recepthantering — läs, lista och spara recept."""

import yaml
from pathlib import Path

RECIPES_DIR = Path(__file__).parent.parent / "data" / "recipes"


def load_all_recipes() -> list:
    """Läs alla recept från data/recipes/ och returnera som lista."""
    recipes = []
    for path in sorted(RECIPES_DIR.glob("*.yaml")):
        with open(path, encoding="utf-8") as f:
            recipes.append(yaml.safe_load(f))
    return recipes


def load_recipe(recipe_id: str) -> dict | None:
    """Läs ett enskilt recept med givet recipe_id."""
    path = RECIPES_DIR / f"{recipe_id}.yaml"
    if not path.exists():
        return None
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def save_recipe(recipe: dict) -> None:
    """Spara ett recept till data/recipes/<recipe_id>.yaml."""
    recipe_id = recipe["recipe_id"]
    path = RECIPES_DIR / f"{recipe_id}.yaml"
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(recipe, f, allow_unicode=True, sort_keys=False)


def delete_recipe(recipe_id: str) -> None:
    """Ta bort ett recept permanent."""
    path = RECIPES_DIR / f"{recipe_id}.yaml"
    if path.exists():
        path.unlink()
