"""Varuhantering — lägg till och ta bort varor i varudatabasen (desktop only)."""

import streamlit as st

from app import items as items_mod, shopping

CATEGORY_NAMES = shopping.CATEGORY_NAMES

_ROLE_LABELS = {
    "ingredient":       "Receptingrediens — bockas in automatiskt från recept",
    "pantry_staple":    "Alltid hemma — ingår i recept men behöver sällan köpas",
    "regular_purchase": "Köps regelbundet — mjölk, ägg, bröd oavsett meny",
    "household":        "Hushållsartikel — ej mat, hanteras manuellt",
}
_ROLE_IDS = list(_ROLE_LABELS.keys())

_UNITS = ["g", "ml", "st", "dl", "kg", "L", "msk", "tsk", "krm", "förp"]


def _invalidate_items_cache() -> None:
    st.session_state.pop("items_db", None)


def _render_add_form() -> None:
    st.subheader("Lägg till vara")

    name = st.text_input("Namn (svenska)", key="vh_name", placeholder="t.ex. havregryn")

    preview_id = items_mod.generate_id(name) if name.strip() else ""
    if preview_id:
        st.caption(f"ID: `{preview_id}`")

    cat_ids   = list(CATEGORY_NAMES.keys())
    cat_labels = [CATEGORY_NAMES[c] for c in cat_ids]
    cat_idx = st.selectbox(
        "Kategori",
        range(len(cat_ids)),
        format_func=lambda i: cat_labels[i],
        key="vh_cat",
    )

    col_unit, col_role = st.columns(2)
    unit = col_unit.selectbox("Enhet", _UNITS, key="vh_unit")
    role_idx = col_role.selectbox(
        "Roll",
        range(len(_ROLE_IDS)),
        format_func=lambda i: _ROLE_LABELS[_ROLE_IDS[i]].split(" — ")[0],
        key="vh_role",
    )
    st.caption(_ROLE_LABELS[_ROLE_IDS[role_idx]].split(" — ", 1)[1])

    synonyms_raw = st.text_input(
        "Synonymer (valfritt, kommaseparerade)",
        key="vh_synonyms",
        placeholder="t.ex. havreflingor, gröt",
    )

    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
    if st.button("Lägg till vara", type="primary", key="vh_add_btn", use_container_width=True):
        if not name.strip():
            st.warning("Ange ett namn.")
            return
        if items_mod.id_exists(preview_id):
            st.error(f"En vara med ID `{preview_id}` finns redan.")
            return
        synonyms = [s for s in synonyms_raw.split(",") if s.strip()] if synonyms_raw else []
        new_id = items_mod.add_item(
            name_sv=name.strip(),
            category=cat_ids[cat_idx],
            unit=unit,
            role=_ROLE_IDS[role_idx],
            synonyms=synonyms,
        )
        _invalidate_items_cache()
        st.success(f"'{name.strip()}' tillagd med ID `{new_id}`.")
        for k in ["vh_name", "vh_synonyms"]:
            st.session_state.pop(k, None)
        st.rerun()


def _render_item_list() -> None:
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.subheader("Befintliga varor")

    items_db = shopping.load_items()

    col_search, col_cat_filter, col_role_filter = st.columns([3, 2, 2])
    search = col_search.text_input(
        "Sök", placeholder="Filtrera på namn…",
        key="vh_search", label_visibility="collapsed"
    ).strip().lower()

    all_cats = ["(alla kategorier)"] + [CATEGORY_NAMES.get(c, c) for c in shopping.CATEGORY_ORDER]
    cat_filter_idx = col_cat_filter.selectbox(
        "Kategori", range(len(all_cats)),
        format_func=lambda i: all_cats[i],
        key="vh_cat_filter", label_visibility="collapsed"
    )
    selected_cat = shopping.CATEGORY_ORDER[cat_filter_idx - 1] if cat_filter_idx > 0 else None

    role_filter_opts = ["(alla roller)"] + [_ROLE_LABELS[r].split(" — ")[0] for r in _ROLE_IDS]
    role_filter_idx = col_role_filter.selectbox(
        "Roll", range(len(role_filter_opts)),
        format_func=lambda i: role_filter_opts[i],
        key="vh_role_filter", label_visibility="collapsed"
    )
    selected_role = _ROLE_IDS[role_filter_idx - 1] if role_filter_idx > 0 else None

    filtered = [
        item for item in items_db.values()
        if (not search or search in item["name_sv"].lower()
            or any(search in s.lower() for s in item.get("synonyms", [])))
        and (selected_cat is None or item.get("category") == selected_cat)
        and (selected_role is None or item.get("role") == selected_role)
    ]

    st.caption(f"{len(filtered)} varor visas av {len(items_db)}")
    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

    if not filtered:
        st.info("Inga varor matchar filtret.")
        return

    confirm_key = "vh_confirm_delete"

    for item in filtered:
        iid  = item["id"]
        name = item["name_sv"]
        cat  = CATEGORY_NAMES.get(item.get("category", ""), item.get("category", ""))
        role_label = _ROLE_LABELS.get(item.get("role", ""), item.get("role", "")).split(" — ")[0]

        col_name, col_cat, col_role, col_del = st.columns([4, 3, 3, 1])
        col_name.markdown(f"**{name}**  \n`{iid}`")
        col_cat.markdown(f"<span style='font-size:0.82rem;color:#7A7A6A'>{cat}</span>", unsafe_allow_html=True)
        col_role.markdown(f"<span style='font-size:0.82rem;color:#7A7A6A'>{role_label}</span>", unsafe_allow_html=True)

        if st.session_state.get(confirm_key) == iid:
            # Bekräftelsesteg
            uses = items_mod.find_recipe_uses(iid)
            if uses:
                col_del.markdown("")
                st.error(
                    f"**{name}** används i {len(uses)} recept: {', '.join(uses)}. "
                    "Redigera recepten innan du tar bort varan."
                )
                if st.button("Avbryt", key=f"vh_cancel_{iid}"):
                    st.session_state.pop(confirm_key, None)
                    st.rerun()
            else:
                col_del.markdown("")
                st.warning(f"Ta bort **{name}** (`{iid}`)? Kan inte ångras.")
                yes_col, no_col = st.columns(2)
                if yes_col.button("Ja, ta bort", key=f"vh_yes_{iid}", type="primary"):
                    items_mod.delete_item(iid)
                    _invalidate_items_cache()
                    st.session_state.pop(confirm_key, None)
                    st.success(f"'{name}' borttagen.")
                    st.rerun()
                if no_col.button("Avbryt", key=f"vh_no_{iid}"):
                    st.session_state.pop(confirm_key, None)
                    st.rerun()
        else:
            if col_del.button("✕", key=f"vh_del_{iid}", help="Ta bort vara"):
                st.session_state[confirm_key] = iid
                st.rerun()


def render() -> None:
    col_back, col_title = st.columns([1, 6])
    if col_back.button("← Tillbaka", key="vh_back"):
        st.session_state.pop("manage_items", None)
        st.rerun()
    col_title.markdown("## Varuhantering")

    st.markdown(
        "<hr style='border-color:#D4DABC; margin:4px 0 16px 0'>",
        unsafe_allow_html=True,
    )

    _render_add_form()

    st.markdown(
        "<hr style='border-color:#D4DABC; margin:16px 0'>",
        unsafe_allow_html=True,
    )

    _render_item_list()
