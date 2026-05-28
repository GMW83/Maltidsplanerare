"""Layout-redigerare för handlingslistan — drag-and-drop av kategorier och varor."""

import streamlit as st
from streamlit_sortables import sort_items

from app import shopping, store_profiles

# Mappning från kategori-ID till visningsnamn (samma som shopping.py)
CATEGORY_NAMES = shopping.CATEGORY_NAMES


def _build_name_to_id(items_db: dict) -> dict:
    """Bygg mapping från visningsnamn → item_id.

    Om två varor har samma name_sv, lägg till (item_id) för att disambiguera.
    """
    # Hitta dubbletter
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


def _build_containers(items_db: dict, profile: dict) -> tuple[list[dict], dict[str, str]]:
    """Bygg container-lista för sort_items och en display_name → item_id mapping.

    Returnerar:
        containers: [{'header': category_display_name, 'items': [display_name, ...]}, ...]
        name_to_id: {display_name: item_id}
    """
    cat_order = profile.get("category_order", shopping.CATEGORY_ORDER)
    item_overrides = profile.get("item_overrides", {})

    name_to_id = _build_name_to_id(items_db)
    id_to_display = {v: k for k, v in name_to_id.items()}

    # Gruppera items per kategori (med overrides)
    by_cat: dict[str, list[str]] = {}
    for item_id, item in items_db.items():
        if item.get("role") not in shopping.INCLUDED_ROLES:
            continue
        cat = item_overrides.get(item_id) or item.get("category", "ovrigt")
        display = id_to_display.get(item_id, item.get("name_sv", item_id))
        by_cat.setdefault(cat, []).append(display)

    for cat in by_cat:
        by_cat[cat].sort()

    # Bygg containers i rätt kategoriordning
    # Ta med alla kategorier som finns i cat_order PLUS eventuella extra (override-kategorier)
    all_cats = list(cat_order)
    for cat in by_cat:
        if cat not in all_cats:
            all_cats.append(cat)

    containers = []
    for cat_id in all_cats:
        items_in_cat = by_cat.get(cat_id, [])
        containers.append({
            "header": CATEGORY_NAMES.get(cat_id, cat_id),
            "items": items_in_cat,
        })

    return containers, name_to_id


def _parse_result(
    sorted_containers: list,
    name_to_id: dict,
    items_db: dict,
    sorted_cat_ids: list[str],
) -> tuple[list[str], dict[str, str]]:
    """Tolka sort_items-resultat tillbaka till category_order och item_overrides.

    sorted_containers: [{'header': display_name, 'items': [...]}, ...]
    sorted_cat_ids: kategori-ID:n i den ordning de sorterades
    """
    # Bygg header → cat_id mapping
    header_to_id = {CATEGORY_NAMES.get(cid, cid): cid for cid in shopping.CATEGORY_ORDER}
    # Lägg till okända kategorier från items_db
    for item in items_db.values():
        cat = item.get("category", "ovrigt")
        header_to_id[CATEGORY_NAMES.get(cat, cat)] = cat

    item_overrides: dict[str, str] = {}

    for container in sorted_containers:
        header = container.get("header", "")
        cat_id = header_to_id.get(header, header)
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
    # Visa kategorier som visningsnamn
    cat_display_list = [CATEGORY_NAMES.get(cid, cid) for cid in cat_order]

    sorted_cat_display = sort_items(cat_display_list, key="cat_sorter")

    # Bygg header→id mapping
    header_to_id = {CATEGORY_NAMES.get(cid, cid): cid for cid in shopping.CATEGORY_ORDER}
    for item in items_db.values():
        cat = item.get("category", "ovrigt")
        header_to_id.setdefault(CATEGORY_NAMES.get(cat, cat), cat)

    sorted_cat_ids = [header_to_id.get(h, h) for h in sorted_cat_display]

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    st.divider()
    st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)

    # ── Varor per kategori ────────────────────────────────────────────────────
    st.markdown("**Varor per kategori** — dra varor mellan kategorier")
    st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)

    containers, name_to_id = _build_containers(items_db, current_profile)

    # Filtrera bort tomma containers för tydlighetens skull
    # (sort_items kräver minst ett element per container annars kan det krascha)
    # Vi behåller ändå tomma containers men markerar dem
    sorted_containers = sort_items(
        containers,
        multi_containers=True,
        key="item_sorter",
    )

    st.divider()

    # ── Spara / Avbryt ────────────────────────────────────────────────────────
    save_col, cancel_col = st.columns([1, 1])

    if save_col.button("Spara layout", type="primary", key="btn_save_layout"):
        new_cat_order, new_overrides = _parse_result(
            sorted_containers,
            name_to_id,
            items_db,
            sorted_cat_ids,
        )
        store_profiles.save_layout(current_profile_id, new_cat_order, new_overrides)
        st.session_state.edit_layout = False
        st.success("Layout sparad!")
        st.rerun()

    if cancel_col.button("Avbryt", key="btn_cancel_layout"):
        st.session_state.edit_layout = False
        st.rerun()
