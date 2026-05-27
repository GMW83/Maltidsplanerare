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

# ── Routing ──────────────────────────────────────────────────────────────────

PAGES = {
    "Hem":          hem.render,
    "Planera":      planera.render,
    "Handlingslista": handlingslista.render,
    "Recept":       recept.render,
}

if "page" not in st.session_state:
    st.session_state.page = "Hem"

# ── Innehåll ─────────────────────────────────────────────────────────────────

PAGES[st.session_state.page]()

# ── Bottenmeny (fast längst ned) ─────────────────────────────────────────────

st.markdown("<div style='height:60px'></div>", unsafe_allow_html=True)

selected = option_menu(
    menu_title=None,
    options=["Hem", "Planera", "Handlingslista", "Recept"],
    icons=["house-fill", "calendar-week-fill", "cart-fill", "book-fill"],
    orientation="horizontal",
    default_index=list(PAGES.keys()).index(st.session_state.page),
    styles={
        "container": {
            "position": "fixed",
            "bottom": "0",
            "left": "0",
            "right": "0",
            "z-index": "9999",
            "padding": "8px 0 12px 0",
            "background-color": "#ffffff",
            "border-top": "1px solid #D4DABC",
            "max-width": "100%",
        },
        "icon":      {"color": "#7A9040", "font-size": "20px"},
        "nav-link":  {
            "font-size": "0.7rem",
            "color": "#7A7A6A",
            "padding": "4px 8px",
        },
        "nav-link-selected": {
            "background-color": "transparent",
            "color": "#3D5016",
            "font-weight": "700",
        },
        "icon--selected": {"color": "#3D5016"},
    },
)

if selected != st.session_state.page:
    st.session_state.page = selected
    st.rerun()
