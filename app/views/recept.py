"""Receptvisare — mobilanpassad, med svenska ingrediensnamn."""

from pathlib import Path

import streamlit as st
import yaml

from app.recipes import load_all_recipes, load_recipe
from app import shopping

PLAN_PATH = Path(__file__).parent.parent.parent / "data" / "weekly_plan.yaml"


def _load_plan() -> dict:
    if PLAN_PATH.exists():
        with open(PLAN_PATH, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}


def render():
    st.title("Recept")

    plan = _load_plan()
    items_db = shopping.load_items()

    if plan.get("meals"):
        recipe_options = {m["title"]: m["recipe_id"] for m in plan["meals"]}
        st.caption("Veckans recept")
    else:
        all_recipes = load_all_recipes()
        recipe_options = {r["title"]: r["recipe_id"] for r in all_recipes}
        st.caption("Alla recept")

    if not recipe_options:
        st.info("Inga recept tillgängliga.")
        return

    selected = st.selectbox(
        "Välj recept",
        list(recipe_options.keys()),
        label_visibility="collapsed",
    )
    recipe = load_recipe(recipe_options[selected])
    if not recipe:
        st.error("Kunde inte ladda receptet.")
        return

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
        amt = ing["amount"]
        amt_str = f"{int(amt) if float(amt) == int(amt) else amt} {ing['unit']}"
        st.markdown(f"- {name} — **{amt_str}**")

    st.subheader("Tillagning")
    steps_html = "".join(
        f"<p style='padding-left:1.6em; text-indent:-1.6em; margin:0 0 7px 0; "
        f"line-height:1.35; font-size:0.9rem; color:#2A2A22'>"
        f"<strong style='color:#2A2A22'>{s['step']}.</strong> {s['text']}</p>"
        for s in recipe.get("instructions", [])
    )
    st.markdown(steps_html, unsafe_allow_html=True)

    if recipe.get("tags"):
        tags_str = " · ".join(recipe["tags"])
        st.markdown(
            f"<div style='height:10px'></div>"
            f"<hr style='border-color:#D4DABC; margin:0 0 8px 0'>"
            f"<p style='font-size:0.8rem; color:#9AA07A; margin:0; "
            f"visibility:visible; opacity:1'>{tags_str}</p>",
            unsafe_allow_html=True,
        )
