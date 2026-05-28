"""Handlingslista — komplett lista, förbockad = behöver köpas."""

import streamlit as st

from app import shopping, store_profiles
from app.views import layout_editor


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


def _render_profile_selector():
    """Rendera kompakt profilväljare med knapp för att öppna layout-editorn."""
    profiles = store_profiles.all_profiles()
    current_id = store_profiles.active_id()

    profile_ids = list(profiles.keys())
    profile_names = [profiles[pid]["name"] for pid in profile_ids]
    current_index = profile_ids.index(current_id) if current_id in profile_ids else 0

    sel_col, btn_col = st.columns([4, 1])

    selected_index = sel_col.selectbox(
        "Butiksprofil",
        options=range(len(profile_ids)),
        format_func=lambda i: profile_names[i],
        index=current_index,
        key="profile_selector",
        label_visibility="collapsed",
    )

    selected_id = profile_ids[selected_index]
    if selected_id != current_id:
        store_profiles.set_active(selected_id)
        st.rerun()

    if btn_col.button("Redigera layout", key="btn_edit_layout"):
        st.session_state.edit_layout = True
        st.rerun()


def render():
    _init_session_state()

    st.title("Handlingslista")

    # Visa layout-editor om edit-läge är aktivt
    if st.session_state.get("edit_layout"):
        items_db = shopping.load_items()
        layout_editor.render(items_db)
        return

    # Profilväljare
    _render_profile_selector()

    active_profile = store_profiles.active()
    full_list = shopping.get_full_list(profile=active_profile)
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
        # Header + spacer i samma element-container — undviker kollaps av separat spacer
        st.markdown(
            f"<p class='cat-header'>{category['category_name']}</p>"
            f"<div style='height:16px'></div>",
            unsafe_allow_html=True,
        )
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
        "<p class='cat-header'>Extra denna vecka</p>"
        "<div style='height:16px'></div>",
        unsafe_allow_html=True,
    )
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
