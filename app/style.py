"""Global CSS-tema för appen — olivgrönt och vitt, mobilanpassat."""

import streamlit as st

CSS = """
<style>
/* ── Dölj Streamlit toolbar och hamburgarmeny ── */
[data-testid="stHeader"]      { display: none !important; }
[data-testid="stToolbar"]     { display: none !important; }
[data-testid="stDecoration"]  { display: none !important; }
#MainMenu                     { display: none !important; }
.stDeployButton               { display: none !important; }

/* ── Bakgrund och layout ── */
.stApp { background: #FAFAF4 !important; }
div.block-container {
    padding: 0.5rem 1rem 4rem 1rem !important;
    max-width: 540px !important;
    margin: 0 auto !important;
}

/* ── Typografi ── */
h1 { color: #3D5016 !important; font-size: 1.7rem !important; margin-bottom: 0.2rem !important; }
h2 { color: #4A6020 !important; font-size: 1.25rem !important; }
h3 { color: #4A6020 !important; font-size: 1.1rem !important; }

/* ── Knappar ── */
.stButton > button {
    background-color: #5B7028 !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.55rem 1.2rem !important;
    font-size: 1rem !important;
    font-weight: 500 !important;
}
.stButton > button:hover  { background-color: #3D5016 !important; }
.stButton > button:active { background-color: #3D5016 !important; }

/* ── Primärknapp (type=primary) ── */
.stButton > button[kind="primary"] {
    background-color: #5B7028 !important;
    font-size: 1.05rem !important;
    padding: 0.7rem 1.4rem !important;
}

/* ── Checkboxar — större för mobil ── */
.stCheckbox { margin: 0 !important; }
.stCheckbox > label {
    font-size: 1.05rem !important;
    padding: 5px 0 !important;
    line-height: 1.5 !important;
    cursor: pointer !important;
}

/* ── Textinput och textarea ── */
.stTextInput > div > div > input,
.stTextArea textarea {
    border-color: #C8D4A0 !important;
    border-radius: 10px !important;
    font-size: 1rem !important;
}

/* ── Selectbox ── */
.stSelectbox > div > div {
    border-color: #C8D4A0 !important;
    border-radius: 10px !important;
}

/* ── Metric-kort ── */
[data-testid="metric-container"] {
    background: #EDF2E0 !important;
    border-radius: 10px !important;
    padding: 8px 10px !important;
}

/* ── Divider ── */
hr { border-color: #D4DABC !important; margin: 0.8rem 0 !important; }

/* ── Hero-sektion (startsida) ── */
.hero-box {
    background: linear-gradient(145deg, #3D5016 0%, #5B7028 55%, #7A9040 100%);
    border-radius: 16px;
    padding: 28px 24px;
    color: white;
    margin-bottom: 20px;
}
.hero-box h1 { color: white !important; font-size: 1.9rem !important; margin: 0 !important; }
.hero-box p  { color: rgba(255,255,255,0.88) !important; margin: 6px 0 0 0 !important; font-size: 1rem; }

/* ── Veckans meny-kort ── */
.meal-card {
    background: white;
    border: 1px solid #D4DABC;
    border-radius: 12px;
    padding: 12px 16px;
    margin-bottom: 8px;
}
.meal-day  { font-size: 0.85rem; color: #7A7A6A; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }
.meal-name { font-size: 1.05rem; color: #2A2A22; font-weight: 500; }

/* ── Handlingslista — förbockad vara ── */
.checked-item label { color: #3D5016 !important; font-weight: 600 !important; }

/* ── Kategorirubriker i handlingslista ── */
.category-header {
    background: #EDF2E0;
    border-radius: 8px;
    padding: 6px 12px;
    margin: 14px 0 4px 0;
    font-size: 0.9rem;
    font-weight: 700;
    color: #3D5016;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}

/* ── Flikar (st.tabs) ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    background-color: #ffffff;
    border-bottom: 2px solid #D4DABC;
    padding: 0;
}
.stTabs [data-baseweb="tab"] {
    font-size: 1rem !important;
    padding: 10px 8px !important;
    color: #7A7A6A !important;
    background: transparent !important;
    border-bottom: 2px solid transparent !important;
    flex: 1;
    justify-content: center;
}
.stTabs [aria-selected="true"] {
    color: #3D5016 !important;
    border-bottom: 2px solid #3D5016 !important;
    font-weight: 700 !important;
    background: transparent !important;
}
.stTabs [data-baseweb="tab-panel"] {
    padding: 12px 0 0 0 !important;
}
</style>
"""


def apply():
    st.markdown(CSS, unsafe_allow_html=True)
