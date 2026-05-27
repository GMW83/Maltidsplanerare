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
    padding: 0.5rem 0.8rem 2rem 0.8rem !important;
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
.stButton > button[kind="primary"] {
    background-color: #5B7028 !important;
    font-size: 1.05rem !important;
    padding: 0.7rem 1.4rem !important;
}

/* ═══════════════════════════════════════════════════
   CHECKBOXAR — tunn olivgrön border, fungerar på mobil
   ═══════════════════════════════════════════════════ */

/* Nollställ marginaler för tät lista */
[data-testid="stCheckbox"] {
    margin: 0 !important;
    padding: 0 !important;
    min-height: 0 !important;
}

/* Label-raden */
[data-testid="stCheckbox"] label {
    display: flex !important;
    align-items: center !important;
    gap: 8px !important;
    padding: 1px 0 !important;
    cursor: pointer !important;
    min-height: 22px !important;
}

/* Texten i labeln — explicit synlig */
[data-testid="stCheckbox"] label p,
[data-testid="stCheckbox"] label span,
[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] {
    font-size: 0.88rem !important;
    color: #2A2A22 !important;
    line-height: 1.3 !important;
    margin: 0 !important;
    padding: 0 !important;
    visibility: visible !important;
    opacity: 1 !important;
    max-width: 100% !important;
    overflow: visible !important;
}

/* BaseWeb wrapper — transparent bakgrund */
[data-testid="stCheckbox"] [role="checkbox"] {
    background-color: transparent !important;
}

/* Visuell ruta — tunn olivgrön border, vit bakgrund.
   Selektorer täcker de vanligaste BaseWeb/Streamlit DOM-varianterna. */
[data-testid="stCheckbox"] [role="checkbox"] > span:first-child,
[data-testid="stCheckbox"] [role="checkbox"] > div:first-child,
[data-testid="stCheckbox"] input[type="checkbox"] + span,
[data-testid="stCheckbox"] input[type="checkbox"] + div {
    width: 16px !important;
    height: 16px !important;
    min-width: 16px !important;
    min-height: 16px !important;
    max-width: 16px !important;
    max-height: 16px !important;
    border: 1.5px solid #9AA07A !important;
    border-radius: 3px !important;
    background-color: white !important;
    box-sizing: border-box !important;
    flex-shrink: 0 !important;
}

/* Inbockad: olivgrön fyllning */
[data-testid="stCheckbox"] [role="checkbox"][aria-checked="true"] > span:first-child,
[data-testid="stCheckbox"] [role="checkbox"][aria-checked="true"] > div:first-child {
    background-color: #5B7028 !important;
    border-color: #5B7028 !important;
}

/* Fallback: native accent-color + rätt storlek */
[data-testid="stCheckbox"] input[type="checkbox"] {
    accent-color: #5B7028 !important;
    width: 16px !important;
    height: 16px !important;
}

/* ── Textinput och textarea ── */
.stTextInput > div > div > input,
.stTextArea textarea {
    border-color: #C8D4A0 !important;
    border-radius: 10px !important;
    font-size: 0.95rem !important;
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

/* ── Tät layout — minska gap mellan element ── */
.stVerticalBlock { gap: 0 !important; }
div[data-testid="element-container"] {
    padding-top: 0 !important;
    padding-bottom: 0 !important;
}

/* ── Markdown-text — explicit synlig (fixar mobil) ── */
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stMarkdownContainer"] ul li,
[data-testid="stMarkdownContainer"] ol li {
    color: #2A2A22 !important;
    font-size: 0.9rem !important;
    line-height: 1.4 !important;
    visibility: visible !important;
    opacity: 1 !important;
    margin-bottom: 0.15rem !important;
}
[data-testid="stMarkdownContainer"] strong {
    color: #2A2A22 !important;
}

/* ── Divider ── */
hr { border-color: #D4DABC !important; margin: 0.6rem 0 !important; }

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
.meal-day  { font-size: 0.8rem; color: #7A7A6A; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }
.meal-name { font-size: 1rem; color: #2A2A22; font-weight: 500; }

/* ── Kategorirubriker i handlingslista ── */
.cat-header {
    font-size: 0.8rem;
    font-weight: 700;
    font-style: italic;
    color: #5B7028;
    margin: 14px 0 16px 0;
    padding-bottom: 3px;
    border-bottom: 1px solid #D4DABC;
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
    padding: 8px 0 0 0 !important;
}
</style>
"""


def apply():
    st.markdown(CSS, unsafe_allow_html=True)
