import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
import yaml

from app.shopping import build_shopping_list

st.set_page_config(page_title="Handlingslista", page_icon="🛒", layout="centered")

PLAN_PATH = Path(__file__).parent.parent.parent / "data" / "weekly_plan.yaml"


def load_plan() -> dict:
    if PLAN_PATH.exists():
        with open(PLAN_PATH, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}


st.title("Handlingslista")

plan = load_plan()

if not plan or not plan.get("meals"):
    st.info("Ingen veckoplan ännu. Gå till Planera veckan och godkänn en meny.")
    st.stop()

st.caption("Veckans meny: " + ", ".join(m["title"] for m in plan["meals"]))
st.divider()

shopping_list = build_shopping_list(plan)

if not shopping_list:
    st.info("Handlingslistan är tom.")
    st.stop()

for category in shopping_list:
    st.subheader(category["category_name"])
    for item in category["items"]:
        amount = item["amount"]
        amount_str = f"{int(amount) if amount == int(amount) else amount} {item['unit']}"
        st.checkbox(
            f"{item['name_sv']} &nbsp; *{amount_str}*",
            key=f"check_{item['id']}",
        )
    st.write("")
