"""Handlingslista — komplett lista, förbockad = behöver köpas."""

import streamlit as st

from app import shopping, store_profiles
from app.views import layout_editor, varuhantering
from app.utils import is_mobile as _is_mobile


def _init_session_state():
    """Synka checkboxtillstånd från fil vid varje render — ger realtidsdelning.
    items_db cachas i session state (ändras ej under körning), load_state läses färskt."""
    if "items_db" not in st.session_state:
        st.session_state["items_db"] = shopping.load_items()
    state = shopping.load_state()
    checked_set = set(state["checked"])
    for item_id in st.session_state["items_db"]:
        st.session_state[f"cb_{item_id}"] = item_id in checked_set


def _on_item_change(item_id: str):
    shopping.set_item_checked(item_id, st.session_state[f"cb_{item_id}"])


def _on_extra_change(idx: int):
    shopping.set_extra_checked(idx, st.session_state[f"cb_extra_{idx}"])


def _on_show_only_change():
    """Ta en ögonblicksbild när filtret slås på, rensa när det slås av.

    Ögonblicksbilden gör att en vara man bockar av i butiken ligger kvar i listan
    tills filtret stängs av — annars försvinner den under fingret.
    """
    if st.session_state.get("show_only_needed"):
        state = shopping.load_state()
        st.session_state["shop_snap_items"] = set(state["checked"])
        st.session_state["shop_snap_extras"] = {
            e["text"] for e in state.get("extras", []) if e.get("checked")
        }
    else:
        st.session_state.pop("shop_snap_items", None)
        st.session_state.pop("shop_snap_extras", None)


def _render_profile_selector():
    """Rendera kompakt profilväljare med knapp för att öppna layout-editorn."""
    profiles = store_profiles.all_profiles()
    current_id = store_profiles.active_id()

    profile_ids = list(profiles.keys())
    profile_names = [profiles[pid]["name"] for pid in profile_ids]
    current_index = profile_ids.index(current_id) if current_id in profile_ids else 0

    mobile = _is_mobile()

    st.selectbox(
        "Butiksprofil",
        options=range(len(profile_ids)),
        format_func=lambda i: profile_names[i],
        index=current_index,
        key="profile_selector",
        label_visibility="collapsed",
    )

    selected_id = profile_ids[st.session_state["profile_selector"]]
    if selected_id != current_id:
        store_profiles.set_active(selected_id)
        st.rerun()

    if not mobile:
        btn_col1, btn_col2 = st.columns(2)
        if btn_col1.button("Redigera layout", key="btn_edit_layout", use_container_width=True):
            st.session_state.edit_layout = True
            st.rerun()
        if btn_col2.button("Hantera varor", key="btn_manage_items", use_container_width=True):
            st.session_state.manage_items = True
            st.rerun()


def render():
    _init_session_state()

    st.title("Handlingslista")

    if st.session_state.get("edit_layout"):
        layout_editor.render(st.session_state["items_db"])
        return

    if st.session_state.get("manage_items"):
        varuhantering.render()
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

    # ── Filter: visa endast det som ska handlas ──────────────────────────────
    show_only = st.checkbox(
        "Visa endast varor att handla",
        key="show_only_needed",
        on_change=_on_show_only_change,
    )
    snap_items = st.session_state.get("shop_snap_items", set())
    snap_extras = st.session_state.get("shop_snap_extras", set())

    # Knapp för att rensa mängder på urcheckade varor
    has_unchecked_with_qty = any(
        not item["checked"] and item.get("quantity")
        for cat in full_list
        for item in cat["items"]
    )
    if has_unchecked_with_qty:
        if st.button("Rensa mängder på urcheckade", key="btn_clear_qty"):
            shopping.clear_quantities_for_unchecked()
            st.rerun()

    # ── Sökfält ─────────────────────────────────────────────────────────────
    search = st.text_input(
        "Sök i listan",
        placeholder="Sök i listan…",
        label_visibility="collapsed",
        key="shopping_search",
    ).strip().lower()

    def _item_visible(item: dict) -> bool:
        if search and search not in item["name_sv"].lower():
            return False
        if show_only and not (item["checked"] or item["id"] in snap_items):
            return False
        return True

    def _extra_visible(extra: dict) -> bool:
        if search and search not in extra["text"].lower():
            return False
        if show_only and not (extra.get("checked") or extra["text"] in snap_extras):
            return False
        return True

    # Ursprungsindex måste bevaras — remove_extra() och cb_extra_-nycklarna bygger på det
    visible_extras = [(idx, e) for idx, e in enumerate(extras) if _extra_visible(e)]
    any_item_visible = False

    # ── Varor per kategori ──────────────────────────────────────────────────
    for category in full_list:
        items_to_show = [it for it in category["items"] if _item_visible(it)]
        if not items_to_show:
            continue
        any_item_visible = True
        # Header + spacer i samma element-container — undviker kollaps av separat spacer
        st.markdown(
            f"<p class='cat-header'>{category['category_name']}</p>"
            f"<div style='height:16px'></div>",
            unsafe_allow_html=True,
        )
        for item in items_to_show:
            iid = item["id"]
            key = f"cb_{iid}"
            if key not in st.session_state:
                st.session_state[key] = item["checked"]
            qty = item.get("quantity")
            if qty:
                qty_str = shopping.format_quantity(qty["amount"], qty["unit"])
                if item["checked"]:
                    label = f"{item['name_sv']}  —  {qty_str}"
                else:
                    label = f"{item['name_sv']}  —  :gray[~~{qty_str}~~]"
            else:
                label = item["name_sv"]
            st.checkbox(
                label,
                key=key,
                on_change=_on_item_change,
                args=(iid,),
            )

    if not any_item_visible and not visible_extras:
        if show_only:
            st.info("Inga varor att handla.")
        elif search:
            st.info(f"Inga varor matchar '{search}'.")

    # ── Extraposter ─────────────────────────────────────────────────────────
    st.markdown(
        "<p class='cat-header'>Extra denna vecka</p>"
        "<div style='height:16px'></div>",
        unsafe_allow_html=True,
    )
    # Visa befintliga extras
    to_remove = None
    for idx, extra in visible_extras:
        # Namngiven container ger CSS-krok så raden inte bryts på mobil
        with st.container(key=f"extra_row_{idx}"):
            col1, col2 = st.columns([8, 1], vertical_alignment="center")
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
        for k in list(st.session_state.keys()):
            if k.startswith("cb_extra_"):
                del st.session_state[k]
        st.rerun()

    # Lägg till ny extrapost
    with st.form("ny_extra", clear_on_submit=True):
        with st.container(key="extra_add_row"):
            col1, col2 = st.columns([8, 1], vertical_alignment="center")
            ny_text = col1.text_input("Lägg till vara", placeholder="Lägg till vara…", label_visibility="collapsed")
            submitted = col2.form_submit_button("＋")
        if submitted and ny_text.strip():
            shopping.add_extra(ny_text)
            st.rerun()
