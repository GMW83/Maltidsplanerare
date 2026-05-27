import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
import yaml

from app.planner import generate_weekly_plan, suggest_replacement

st.set_page_config(page_title="Planera veckan", page_icon="📅", layout="centered")

PLAN_PATH = Path(__file__).parent.parent.parent / "data" / "weekly_plan.yaml"


def load_plan() -> dict:
    if PLAN_PATH.exists():
        with open(PLAN_PATH, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}


def save_plan(plan: dict) -> None:
    with open(PLAN_PATH, "w", encoding="utf-8") as f:
        yaml.dump(plan, f, allow_unicode=True, sort_keys=False)


if "plan" not in st.session_state:
    st.session_state.plan = load_plan()

st.title("Planera veckan")

user_input = st.text_area(
    "Vad vill ni äta den här veckan?",
    placeholder="t.ex. 'något asiatiskt, något med kyckling, lite enklare på fredagen'",
    height=120,
)

if st.button("Generera förslag", type="primary", use_container_width=True):
    if user_input.strip():
        with st.spinner("Genererar förslag..."):
            try:
                st.session_state.plan = generate_weekly_plan(user_input)
            except Exception as e:
                st.error(f"Fel: {e}")
    else:
        st.warning("Berätta vad ni vill äta så genererar AI ett förslag.")

if st.session_state.plan.get("meals"):
    st.divider()
    st.subheader("Förslag på veckomeny")

    for i, meal in enumerate(st.session_state.plan["meals"]):
        col1, col2 = st.columns([4, 1])
        col1.markdown(f"**{meal['day'].capitalize()}** &nbsp; {meal['title']}")
        if col2.button("Byt ut", key=f"replace_{i}", use_container_width=True):
            with st.spinner(f"Föreslår nytt alternativ för {meal['day']}..."):
                try:
                    replacement = suggest_replacement(meal["day"], st.session_state.plan)
                    st.session_state.plan["meals"][i] = replacement
                    st.rerun()
                except Exception as e:
                    st.error(f"Fel: {e}")

    st.divider()
    if st.button("Godkänn veckoplan", type="primary", use_container_width=True):
        save_plan(st.session_state.plan)
        st.success("Veckoplan sparad! Gå till Handlingslistan.")
