"""Startsida — hero med veckans meny."""

from datetime import date

import streamlit as st

from app.planner import load_plan, current_week_start, week_start_for_offset


def render():
    this_week = current_week_start()
    next_week = week_start_for_offset(1)
    options = [this_week, next_week]

    idx = st.radio(
        "Visa",
        options=[0, 1],
        format_func=lambda i: "Denna vecka" if options[i] == this_week else "Nästa vecka",
        horizontal=True,
        key="hem_week_radio",
        label_visibility="collapsed",
    )
    selected_week = options[idx]

    plan = load_plan(selected_week)
    meals = plan.get("meals", [])
    today = date.today()
    week_nr = selected_week.isocalendar()[1]

    if meals:
        hero_sub = "Veckans middagar är planerade" if selected_week == this_week else "Nästa veckas meny är planerad"
        hero_text = f"Vecka {week_nr}" + (f" · {today.strftime('%d/%m')}" if selected_week == this_week else "")
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

    st.markdown(
        "<div style='text-align:center; margin-top:32px'>"
        "<a href='/app/static/manual.html' target='_blank' "
        "style='color:#6B7C3E; font-size:0.82rem; text-decoration:none;'>"
        "📖 Användarmanual</a></div>",
        unsafe_allow_html=True,
    )
