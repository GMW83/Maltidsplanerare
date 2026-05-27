import streamlit as st

st.set_page_config(
    page_title="Maltidsplanerare",
    page_icon="🍽️",
    layout="centered",
)

pages = {
    "Planera veckan": "app/pages/plan.py",
    "Handlingslista": "app/pages/shopping.py",
    "Recept": "app/pages/recipes.py",
}

st.title("Måltidsplanerare")
st.info("Välj en sida i sidomenyn för att komma igång.")
