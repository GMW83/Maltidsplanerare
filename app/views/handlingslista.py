"""Handlingslista — komplett lista, förbockad = behöver köpas."""

import streamlit as st

from app import shopping


def _init_session_state():
    """Läs tillstånd från fil och initiera session state (en gång per session)."""
    if st.session_state.get("shopping_loaded"):
        return
    state = shopping.load_state()
    checked_set = set(state["checked"])
    items_db = shopping.load_items()
    for item_id in items_db:
        key = f"cb_{item_id}"
        if key not in st.session_state:
            st.session_state[key] = item_id in checked_set
    st.session_state.shopping_loaded = True


def _on_item_change(item_id: str):
    shopping.set_item_checked(item_id, st.session_state[f"cb_{item_id}"])


def _on_extra_change(idx: int):
    shopping.set_extra_checked(idx, st.session_state[f"cb_extra_{idx}"])


def render():
    _init_session_state()

    st.title("Handlingslista")

    full_list = shopping.get_full_list()
    state = shopping.load_state()
    extras = state.get("extras", [])

    # Räkna förbockade
    total_checked = sum(
        1 for cat in full_list for item in cat["items"] if item["checked"]
    ) + sum(1 for e in extras if e.get("checked"))

    if total_checked:
        st.caption(f"{total_checked} varor att handla")
    else:
        st.caption("Inga varor markerade — bocka i vad som behövs")

    # ── Varor per kategori ──────────────────────────────────────────────────
    for category in full_list:
        st.markdown(
            f"<p class='cat-header'>{category['category_name']}</p>",
            unsafe_allow_html=True,
        )
        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
        for item in category["items"]:
            iid = item["id"]
            key = f"cb_{iid}"
            if key not in st.session_state:
                st.session_state[key] = item["checked"]
            st.checkbox(
                item["name_sv"],
                key=key,
                on_change=_on_item_change,
                args=(iid,),
            )

    # ── Extraposter ─────────────────────────────────────────────────────────
    st.markdown(
        "<p class='cat-header'>Extra denna vecka</p>",
        unsafe_allow_html=True,
    )
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    # Visa befintliga extras
    to_remove = None
    for idx, extra in enumerate(extras):
        col1, col2 = st.columns([5, 1])
        key = f"cb_extra_{idx}"
        if key not in st.session_state:
            st.session_state[key] = extra.get("checked", True)
        col1.checkbox(
            extra["text"],
            key=key,
            on_change=_on_extra_change,
            args=(idx,),
        )
        if col2.button("✕", key=f"del_extra_{idx}", help="Ta bort"):
            to_remove = idx

    if to_remove is not None:
        shopping.remove_extra(to_remove)
        st.rerun()

    # Lägg till ny extrapost
    with st.form("ny_extra", clear_on_submit=True):
        col1, col2 = st.columns([4, 1])
        ny_text = col1.text_input("", placeholder="Lägg till vara…", label_visibility="collapsed")
        submitted = col2.form_submit_button("＋")
        if submitted and ny_text.strip():
            shopping.add_extra(ny_text)
            st.rerun()
