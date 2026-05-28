"""Startsida — hero med veckans meny."""

from datetime import date

import streamlit as st

from app.planner import load_plan, is_plan_current, clear_plan, current_week_start


def render():
    plan = load_plan()

    # Auto-expire: nollställ om planen tillhör en passerad vecka
    ws = plan.get("week_start")
    if ws and not is_plan_current(plan):
        clear_plan()
        plan = {"week_start": None, "meals": []}

    meals = plan.get("meals", [])
    today = date.today()
    week_nr = today.isocalendar()[1]

    if meals:
        # Visa vilken vecka planen gäller (kan vara nästa vecka)
        plan_ws = plan.get("week_start")
        if isinstance(plan_ws, str):
            from datetime import date as d
            plan_ws = d.fromisoformat(plan_ws)
        plan_week_nr = plan_ws.isocalendar()[1] if plan_ws else week_nr
        if plan_week_nr != week_nr:
            hero_sub = f"Meny planerad för vecka {plan_week_nr}"
        else:
            hero_sub = "Veckans middagar är planerade"
        hero_text = f"Vecka {week_nr} · {today.strftime('%d/%m')}"
    else:
        hero_text = f"Vecka {week_nr}"
        hero_sub = "Ingen meny planerad"

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
