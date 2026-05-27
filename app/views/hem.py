"""Startsida — hero med veckans meny."""

from datetime import date
from pathlib import Path

import streamlit as st
import yaml

PLAN_PATH = Path(__file__).parent.parent.parent / "data" / "weekly_plan.yaml"

DAYS_SV = ["måndag", "tisdag", "onsdag", "torsdag", "fredag", "lördag", "söndag"]


def _load_plan() -> dict:
    if PLAN_PATH.exists():
        with open(PLAN_PATH, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}


def render():
    plan = _load_plan()
    meals = plan.get("meals", [])

    today = date.today()
    week_nr = today.isocalendar()[1]
    date_str = today.strftime("%-d %B %Y").lower() if hasattr(today, "strftime") else str(today)

    if meals:
        hero_text = f"Vecka {week_nr} · {today.strftime('%d/%m')}"
        hero_sub = "Veckans middagar är planerade"
    else:
        hero_text = f"Vecka {week_nr}"
        hero_sub = "Ingen meny planerad ännu"

    st.markdown(
        f"""
        <div class="hero-box">
            <h1>🍽️ Måltidsplanerare</h1>
            <p>{hero_text} &nbsp;·&nbsp; {hero_sub}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if meals:
        for meal in meals:
            st.markdown(
                f"""
                <div class="meal-card">
                    <div class="meal-day">{meal['day'].capitalize()}</div>
                    <div class="meal-name">{meal['title']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.info("Gå till Planera-fliken för att skapa veckans meny.")
