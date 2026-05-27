"""Planera veckan — AI-förslag, byt ut dagar, godkänn."""

from pathlib import Path

import streamlit as st
import yaml

from app.planner import generate_weekly_plan, suggest_replacement
from app import shopping

PLAN_PATH = Path(__file__).parent.parent.parent / "data" / "weekly_plan.yaml"


def _load_plan() -> dict:
    if PLAN_PATH.exists():
        with open(PLAN_PATH, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}


def _save_plan(plan: dict) -> None:
    with open(PLAN_PATH, "w", encoding="utf-8") as f:
        yaml.dump(plan, f, allow_unicode=True, sort_keys=False)


def render():
    st.title("Planera veckan")

    if "plan_draft" not in st.session_state:
        st.session_state.plan_draft = {}

    user_input = st.text_area(
        "Vad vill ni äta den här veckan?",
        placeholder="t.ex. 'något asiatiskt, lite enklare på fredagen, vi har bönar hemma'",
        height=110,
        label_visibility="visible",
    )

    if st.button("Generera förslag", type="primary", use_container_width=True):
        if user_input.strip():
            with st.spinner("Genererar förslag..."):
                try:
                    st.session_state.plan_draft = generate_weekly_plan(user_input)
                except Exception as e:
                    st.error(f"Kunde inte generera förslag: {e}")
        else:
            st.warning("Skriv vad ni är sugna på så hjälper AI:n till.")

    draft = st.session_state.plan_draft
    if not draft.get("meals"):
        return

    st.divider()
    st.subheader("Förslag")

    for i, meal in enumerate(draft["meals"]):
        col1, col2 = st.columns([4, 1])
        col1.markdown(
            f"<div class='meal-card'>"
            f"<div class='meal-day'>{meal['day'].capitalize()}</div>"
            f"<div class='meal-name'>{meal['title']}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )
        if col2.button("↺", key=f"rep_{i}", help=f"Byt ut {meal['day']}"):
            with st.spinner("Föreslår alternativ..."):
                try:
                    replacement = suggest_replacement(meal["day"], draft)
                    st.session_state.plan_draft["meals"][i] = replacement
                    st.rerun()
                except Exception as e:
                    st.error(f"Fel: {e}")

    st.divider()
    if st.button("✓  Godkänn och spara veckoplan", type="primary", use_container_width=True):
        _save_plan(draft)
        shopping.apply_meal_plan(draft)
        # Återställ shopping session state så listan laddas om
        for key in list(st.session_state.keys()):
            if key.startswith("cb_"):
                del st.session_state[key]
        st.session_state.shopping_loaded = False
        st.success("Veckoplan sparad och handlingslista uppdaterad!")
