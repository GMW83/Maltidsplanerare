"""Planera veckan — välj vecka och dagar, AI-förslag, godkänn."""

from datetime import date, timedelta

import streamlit as st

from app import settings as app_settings
from app import shopping
from app.planner import (
    current_week_start,
    generate_weekly_plan,
    is_plan_current,
    load_plan,
    save_plan,
    suggest_replacement,
    week_start_for_offset,
)

DAYS_SV  = ["måndag", "tisdag", "onsdag", "torsdag", "fredag", "lördag", "söndag"]
DAYS_ABB = ["Mån", "Tis", "Ons", "Tor", "Fre", "Lör", "Sön"]


def _week_label(ws: date) -> str:
    nr = ws.isocalendar()[1]
    today = date.today()
    cws = current_week_start()
    if ws == cws:
        return f"Denna vecka (v. {nr})"
    return f"Nästa vecka (v. {nr})"


def _day_selector(selected_week_start: date) -> list[str]:
    """Rendera dagväljare och returnera lista med valda dagnamn (sv)."""
    today = date.today()
    is_current_week = selected_week_start == current_week_start()

    st.markdown("**Välj dagar:**")
    st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)
    cols = st.columns(7)
    selected = []

    for i, (day, abb) in enumerate(zip(DAYS_SV, DAYS_ABB)):
        day_date = selected_week_start + timedelta(days=i)
        disabled = is_current_week and day_date <= today

        with cols[i]:
            if disabled:
                st.markdown(
                    f"<div style='text-align:center;color:#bbb;font-size:0.78rem;"
                    f"padding-top:6px'>{abb}</div>",
                    unsafe_allow_html=True,
                )
            else:
                checked = st.checkbox(abb, key=f"day_sel_{i}", value=True)
                if checked:
                    selected.append(day)

    return selected


def render():
    st.title("Planera veckan")

    if "plan_draft" not in st.session_state:
        st.session_state.plan_draft = {}
    if "draft_week_start" not in st.session_state:
        st.session_state.draft_week_start = None

    # ── Veckoväljare ──────────────────────────────────────────────────────────
    this_week = current_week_start()
    next_week = week_start_for_offset(1)

    week_options = [this_week, next_week]
    week_index = st.radio(
        "Planera för:",
        options=[0, 1],
        format_func=lambda i: _week_label(week_options[i]),
        horizontal=True,
        key="week_radio",
    )
    selected_week = week_options[week_index]

    # Varna om en plan redan finns för vald vecka
    existing = load_plan()
    existing_ws = existing.get("week_start")
    if isinstance(existing_ws, str):
        existing_ws = date.fromisoformat(existing_ws)
    if existing_ws == selected_week and existing.get("meals"):
        st.warning(
            f"En plan finns redan för v. {selected_week.isocalendar()[1]}. "
            "Om du godkänner ett nytt förslag skrivs den befintliga över."
        )

    # ── Dagväljare ────────────────────────────────────────────────────────────
    selected_days = _day_selector(selected_week)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ── Antal personer ────────────────────────────────────────────────────────
    saved_size = app_settings.get("household_size")
    household_size = st.number_input(
        "Antal personer",
        min_value=1,
        max_value=12,
        value=saved_size,
        step=1,
        key="household_size_input",
    )
    if int(household_size) != saved_size:
        app_settings.set_value("household_size", int(household_size))

    # ── Fritext-input ─────────────────────────────────────────────────────────
    user_input = st.text_area(
        "Vad vill ni äta?",
        placeholder="t.ex. 'något asiatiskt, lite enklare på fredagen, vi har bönar hemma'",
        height=100,
        label_visibility="visible",
    )

    if st.button("Generera förslag", type="primary", use_container_width=True):
        if not selected_days:
            st.warning("Välj minst en dag att planera för.")
        elif not user_input.strip():
            st.warning("Skriv vad ni är sugna på så hjälper AI:n till.")
        else:
            with st.spinner("Genererar förslag..."):
                try:
                    draft = generate_weekly_plan(user_input, selected_days)
                    st.session_state.plan_draft = draft
                    st.session_state.draft_week_start = selected_week.isoformat()
                except Exception as e:
                    st.error(f"Kunde inte generera förslag: {e}")

    draft = st.session_state.plan_draft
    if not draft.get("meals"):
        return

    # ── Förslag ───────────────────────────────────────────────────────────────
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
        week_start_str = st.session_state.get("draft_week_start") or this_week.isoformat()
        plan_to_save = {
            "week_start": date.fromisoformat(week_start_str),
            "meals": draft["meals"],
        }
        save_plan(plan_to_save)
        unmatched = shopping.apply_meal_plan(draft, household_size=int(household_size))
        # Återställ shopping session state
        for key in list(st.session_state.keys()):
            if key.startswith("cb_"):
                del st.session_state[key]
        st.session_state.plan_draft = {}
        st.success("Veckoplan sparad och handlingslista uppdaterad!")
        if unmatched:
            st.info(
                f"**{len(unmatched)} ingrediens(er) saknas i varudatabasen** och har lagts till "
                f"under 'Extra denna vecka' med beräknad mängd: {', '.join(unmatched)}"
            )
        st.rerun()
