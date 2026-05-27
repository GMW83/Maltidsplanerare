import streamlit as st

st.set_page_config(
    page_title="Måltidsplanerare",
    page_icon="🍽️",
    layout="centered",
)

st.title("Måltidsplanerare")
st.markdown(
    """
    Välkommen! Använd menyn till vänster för att navigera.

    - **Planera veckan** — berätta vad ni är sugna på, få ett AI-förslag och godkänn menyn
    - **Handlingslista** — alla ingredienser ibockade och sorterade efter butiksordning
    - **Recept** — läs veckans recept, fungerar på mobil
    """
)
