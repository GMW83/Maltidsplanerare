import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st

from app import style
from app.views import hem, planera, handlingslista, recept

st.set_page_config(
    page_title="Måltidsplanerare",
    page_icon="🍽️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

style.apply()

tab_hem, tab_planera, tab_lista, tab_recept = st.tabs([
    "🏠 Hem",
    "📅 Planera",
    "🛒 Lista",
    "📖 Recept",
])

with tab_hem:
    hem.render()

with tab_planera:
    planera.render()

with tab_lista:
    handlingslista.render()

with tab_recept:
    recept.render()
