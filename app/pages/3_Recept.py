import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
import yaml

from app.recipes import load_all_recipes, load_recipe

st.set_page_config(page_title="Recept", page_icon="📖", layout="centered")

PLAN_PATH = Path(__file__).parent.parent.parent / "data" / "weekly_plan.yaml"
DATA_DIR = Path(__file__).parent.parent.parent / "data"


def load_plan() -> dict:
    if PLAN_PATH.exists():
        with open(PLAN_PATH, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}


def load_items() -> dict:
    with open(DATA_DIR / "items.yaml", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return {item["id"]: item for item in data.get("items", [])}


st.title("Recept")

plan = load_plan()

if plan and plan.get("meals"):
    recipe_options = {m["title"]: m["recipe_id"] for m in plan["meals"]}
    st.caption("Veckans recept")
else:
    all_recipes = load_all_recipes()
    recipe_options = {r["title"]: r["recipe_id"] for r in all_recipes}
    st.caption("Alla recept")

if not recipe_options:
    st.info("Inga recept tillgängliga.")
    st.stop()

selected_title = st.selectbox("Välj recept", list(recipe_options.keys()), label_visibility="collapsed")
recipe = load_recipe(recipe_options[selected_title])

if not recipe:
    st.error("Receptet kunde inte laddas.")
    st.stop()

items_db = load_items()
meta = recipe.get("metadata", {})

st.header(recipe["title"])

col1, col2, col3 = st.columns(3)
col1.metric("Portioner", recipe.get("servings", "?"))
col2.metric("Tid", f"{meta.get('cook_time_minutes', '?')} min")
col3.metric("Svårighetsgrad", f"{meta.get('difficulty', '?')}/3")

st.subheader("Ingredienser")
for ing in recipe.get("ingredients", []):
    item = items_db.get(ing["ingredient_id"])
    name = item["name_sv"] if item else ing["ingredient_id"].replace("_", " ")
    amount = ing["amount"]
    amount_str = f"{int(amount) if amount == int(amount) else amount} {ing['unit']}"
    st.markdown(f"- {name} — **{amount_str}**")

st.subheader("Tillagning")
for step in recipe.get("instructions", []):
    st.markdown(f"**{step['step']}.** {step['text']}")

if recipe.get("tags"):
    st.divider()
    st.caption("Taggar: " + " · ".join(recipe["tags"]))
