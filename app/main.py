import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from streamlit_option_menu import option_menu

from app import style
from app.views import hem, planera, handlingslista, recept

st.set_page_config(
    page_title="Måltidsplanerare",
    page_icon="🍽️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

style.apply()

PAGES = {
    "Hem":            hem.render,
    "Planera":        planera.render,
    "Handlingslista": handlingslista.render,
    "Recept":         recept.render,
}

if "page" not in st.session_state:
    st.session_state.page = "Hem"

# ── Navigation (topp) ─────────────────────────────────────────────────────────

selected = option_menu(
    menu_title=None,
    options=list(PAGES.keys()),
    icons=["house-fill", "calendar-week-fill", "cart-fill", "book-fill"],
    orientation="horizontal",
    default_index=list(PAGES.keys()).index(st.session_state.page),
    styles={
        "container": {
            "padding": "4px 0",
            "background-color": "#ffffff",
            "border-bottom": "1px solid #D4DABC",
            "margin-bottom": "12px",
        },
        "icon":            {"color": "#8FA040", "font-size": "18px"},
        "nav-link":        {"font-size": "0.72rem", "color": "#7A7A6A", "padding": "4px 6px"},
        "nav-link-selected": {"background-color": "#EDF2E0", "color": "#3D5016", "font-weight": "700", "border-radius": "8px"},
        "icon--selected":  {"color": "#3D5016"},
    },
)

if selected != st.session_state.page:
    st.session_state.page = selected
    st.rerun()

# ── Innehåll ──────────────────────────────────────────────────────────────────

PAGES[st.session_state.page]()
