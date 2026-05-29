"""Layout-redigerare för handlingslistan — drag-and-drop av kategorier och varor."""

import streamlit as st
from streamlit_sortables import sort_items

from app import shopping, store_profiles

CATEGORY_NAMES = shopping.CATEGORY_NAMES


def _is_mobile() -> bool:
    try:
        ua = st.context.headers.get("user-agent", "").lower()
        return any(kw in ua for kw in ("mobile", "android", "iphone", "ipad", "ipod"))
    except Exception:
        return False


def _build_name_to_id(items_db: dict) -> dict:
    name_counts: dict[str, int] = {}
    for item in items_db.values():
        n = item.get("name_sv", "")
        name_counts[n] = name_counts.get(n, 0) + 1

    name_to_id: dict[str, str] = {}
    for item_id, item in items_db.items():
        n = item.get("name_sv", "")
        display = f"{n} ({item_id})" if name_counts[n] > 1 else n
        name_to_id[display] = item_id
    return name_to_id


def _build_containers(
    items_db: dict, profile: dict
) -> tuple[list[dict], dict[str, str], dict[str, str]]:
    """Bygg container-lista för sort_items.

    Returnerar (containers, name_to_id, header_to_cat_id).
    """
    cat_order = profile.get("category_order", shopping.CATEGORY_ORDER)
    item_overrides = profile.get("item_overrides", {})
    category_names = profile.get("category_names", {})

    name_to_id = _build_name_to_id(items_db)
    id_to_display = {v: k for k, v in name_to_id.items()}

    by_cat: dict[str, list[str]] = {}
    for item_id, item in items_db.items():
        if item.get("role") not in shopping.INCLUDED_ROLES:
            continue
        cat = item_overrides.get(item_id) or item.get("category", "ovrigt")
        display = id_to_display.get(item_id, item.get("name_sv", item_id))
        by_cat.setdefault(cat, []).append(display)

    for cat in by_cat:
        by_cat[cat].sort()

    all_cats = list(cat_order)
    for cat in by_cat:
        if cat not in all_cats:
            all_cats.append(cat)

    header_to_cat_id: dict[str, str] = {}
    containers = []
    for cat_id in all_cats:
        display_name = category_names.get(cat_id) or CATEGORY_NAMES.get(cat_id, cat_id)
        header_to_cat_id[display_name] = cat_id
        containers.append({
            "header": display_name,
            "items": by_cat.get(cat_id, []),
        })

    return containers, name_to_id, header_to_cat_id


def _parse_result(
    sorted_containers: list,
    name_to_id: dict,
    items_db: dict,
    sorted_cat_ids: list[str],
    header_to_cat_id: dict[str, str],
) -> tuple[list[str], dict[str, str]]:
    """Tolka sort_items-resultat tillbaka till category_order och item_overrides."""
    item_overrides: dict[str, str] = {}

    for container in sorted_containers:
        header = container.get("header", "")
        cat_id = header_to_cat_id.get(header, header)
        for display_name in container.get("items", []):
            item_id = name_to_id.get(display_name)
            if item_id is None:
                continue
            default_cat = items_db.get(item_id, {}).get("category", "ovrigt")
            if cat_id != default_cat:
                item_overrides[item_id] = cat_id

    return sorted_cat_ids, item_overrides


def render(items_db: dict):
    """Rendera layout-editorn. Anropas från handlingslista.py vid edit-läge."""
    data = store_profiles.load()
    profiles = data.get("profiles", {})
    current_profile_id = data.get("active_profile", "standard")
    current_profile = profiles.get(current_profile_id, {})

    st.subheader("Redigera butiksprofil")

    # ── Profilhantering ───────────────────────────────────────────────────────
    st.markdown("**Profil**")
    st.markdown("<div style='height:30px'></div>", unsafe_allow_html=True)
    mgmt_col1, mgmt_col2, mgmt_col3, mgmt_col4 = st.columns([3, 1, 1, 1])

    new_name = mgmt_col1.text_input(
        "Profilnamn",
        value=current_profile.get("name", current_profile_id),
        key="editor_profile_name",
        label_visibility="collapsed",
    )
    if mgmt_col2.button("Spara namn", key="btn_save_name"):
        try:
            store_profiles.rename(current_profile_id, new_name)
            st.success("Namn sparat.")
            st.rerun()
        except ValueError as e:
            st.error(str(e))

    if mgmt_col3.button("Ny profil", key="btn_new_profile"):
        new_id = store_profiles.create(new_name if new_name else "Ny profil")
        store_profiles.set_active(new_id)
        st.rerun()

    if mgmt_col4.button("Ta bort", key="btn_delete_profile"):
        try:
            store_profiles.delete(current_profile_id)
            st.rerun()
        except ValueError as e:
            st.error(str(e))

    st.divider()
    st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)

    # ── Kategoriordning ───────────────────────────────────────────────────────
    st.markdown("**Kategoriordning** — dra för att ändra ordning")
    st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)

    cat_order = current_profile.get("category_order", shopping.CATEGORY_ORDER)
    category_names = current_profile.get("category_names", {})

    cat_display_list = [
        category_names.get(cid) or CATEGORY_NAMES.get(cid, cid)
        for cid in cat_order
    ]
    cat_display_to_id = dict(zip(cat_display_list, cat_order))

    sorted_cat_display = sort_items(cat_display_list, key="cat_sorter")
    sorted_cat_ids = [cat_display_to_id.get(h, h) for h in sorted_cat_display]

    if not _is_mobile():
        st.markdown(
            "<div style='height:20px'></div>"
            "<hr style='border-color:#D4DABC; margin:0'>"
            "<div style='height:40px'></div>"
            "<strong>Kategorier</strong> — byt namn, lägg till och ta bort"
            "<div style='height:16px'></div>",
            unsafe_allow_html=True,
        )

    if not _is_mobile():
        confirm_del_cat = st.session_state.get("confirm_del_cat")

        for cat_id in cat_order:
            current_cat_name = category_names.get(cat_id) or CATEGORY_NAMES.get(cat_id, cat_id)

            if confirm_del_cat == cat_id:
                st.warning(
                    f"Ta bort **{current_cat_name}**? "
                    "Varor i kategorin återgår till sin standardkategori."
                )
                yes_col, no_col = st.columns(2)
                if yes_col.button("Ja, ta bort", key=f"cat_del_yes_{cat_id}", use_container_width=True):
                    try:
                        store_profiles.delete_category(current_profile_id, cat_id)
                        st.session_state.pop("confirm_del_cat", None)
                    except ValueError as e:
                        st.error(str(e))
                    st.rerun()
                if no_col.button("Avbryt", key=f"cat_del_no_{cat_id}", use_container_width=True):
                    st.session_state.pop("confirm_del_cat", None)
                    st.rerun()
            else:
                col_name, col_save, col_del = st.columns([5, 2, 1])
                edited_name = col_name.text_input(
                    "",
                    value=current_cat_name,
                    key=f"cat_name_{cat_id}",
                    label_visibility="collapsed",
                )
                if col_save.button("Spara", key=f"cat_save_{cat_id}", use_container_width=True):
                    if edited_name.strip():
                        store_profiles.set_category_name(
                            current_profile_id, cat_id, edited_name.strip()
                        )
                        st.rerun()
                if col_del.button("✕", key=f"cat_del_{cat_id}", help="Ta bort kategori", use_container_width=True):
                    st.session_state["confirm_del_cat"] = cat_id
                    st.rerun()

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

        with st.form("add_category_form", clear_on_submit=True):
            form_col1, form_col2 = st.columns([4, 1])
            new_cat_name = form_col1.text_input(
                "",
                placeholder="Lägg till ny kategori…",
                label_visibility="collapsed",
            )
            if form_col2.form_submit_button("＋"):
                if new_cat_name.strip():
                    store_profiles.add_category(current_profile_id, new_cat_name.strip())
                    st.rerun()

        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
        st.divider()
        st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)

    # ── Varor per kategori ────────────────────────────────────────────────────
    st.markdown("**Varor per kategori** — dra varor mellan kategorier")
    st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)

    # Reload profile after potential immediate saves above
    current_profile = store_profiles.load()["profiles"].get(current_profile_id, {})

    containers, name_to_id, header_to_cat_id = _build_containers(items_db, current_profile)

    sorted_containers = sort_items(
        containers,
        multi_containers=True,
        key="item_sorter",
    )

    st.markdown(
        "<div style='height:40px'></div>"
        "<hr style='border-color:#D4DABC; margin:0'>"
        "<div style='height:8px'></div>",
        unsafe_allow_html=True,
    )

    # ── Spara / Avbryt ────────────────────────────────────────────────────────
    save_col, cancel_col = st.columns([1, 1])

    if save_col.button("Spara layout", type="primary", key="btn_save_layout"):
        new_cat_order, new_overrides = _parse_result(
            sorted_containers,
            name_to_id,
            items_db,
            sorted_cat_ids,
            header_to_cat_id,
        )
        store_profiles.save_layout(current_profile_id, new_cat_order, new_overrides)
        st.session_state.edit_layout = False
        st.success("Layout sparad!")
        st.rerun()

    if cancel_col.button("Avbryt", key="btn_cancel_layout"):
        st.session_state.edit_layout = False
        st.rerun()
