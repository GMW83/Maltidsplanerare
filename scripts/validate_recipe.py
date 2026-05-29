"""Validera att en receptfil följer schemat."""

import sys
import yaml
from pathlib import Path

REQUIRED_FIELDS = ["recipe_id", "title", "servings", "ingredients", "instructions"]


def validate(path: Path) -> list[str]:
    with open(path, encoding="utf-8") as f:
        recipe = yaml.safe_load(f)
    errors = [f"Saknar fält: {field}" for field in REQUIRED_FIELDS if field not in recipe]
    return errors


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Användning: python validate_recipe.py <path-till-recept.yaml>")
        sys.exit(1)
    errors = validate(Path(sys.argv[1]))
    if errors:
        for e in errors:
            print(f"FEL: {e}")
        sys.exit(1)
    print("OK")
