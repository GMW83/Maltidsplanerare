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
_UNITS    = ["g", "ml", "st", "dl", "kg", "L", "msk", "tsk", "krm", "förp"]
_PAGE_SIZE = 50


def _invalidate_items_cache() -> None:
    st.session_state.pop("items_db", None)


# ── Lägg till-formulär ────────────────────────────────────────────────────────

def _render_add_form() -> None:
    st.subheader("Lägg till vara")

    name = st.text_input("Namn (svenska)", key="vh_name", placeholder="t.ex. havregryn")

    preview_id = items_mod.generate_id(name) if name.strip() else ""
    if preview_id:
        st.caption(f"ID: `{preview_id}`")

    cat_ids    = list(CATEGORY_NAMES.keys())
    cat_labels = [CATEGORY_NAMES[c] for c in cat_ids]
    cat_idx = st.selectbox(
        "Kategori",
        range(len(cat_ids)),
        format_func=lambda i: cat_labels[i],
        key="vh_cat",
    )

    col_unit, col_role = st.columns(2)
    unit     = col_unit.selectbox("Enhet", _UNITS, key="vh_unit")
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
        if items_mod.name_exists(name):
            st.error(f"En vara med namnet '{name.strip()}' finns redan i databasen.")
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


# ── Befintliga varor ──────────────────────────────────────────────────────────

def _render_item_list() -> None:
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.subheader("Befintliga varor")

    items_db = shopping.load_items()
    all_items = list(items_db.values())

    # ── Filter ────────────────────────────────────────────────────────────────
    col_search, col_cat_filter, col_role_filter = st.columns([3, 2, 2])
    search = col_search.text_input(
        "Sök", placeholder="Filtrera på namn…",
        key="vh_search", label_visibility="collapsed",
    ).strip().lower()

    all_cats   = ["(alla kategorier)"] + [CATEGORY_NAMES.get(c, c) for c in shopping.CATEGORY_ORDER]
    cat_fi     = col_cat_filter.selectbox(
        "Kategori", range(len(all_cats)),
        format_func=lambda i: all_cats[i],
        key="vh_cat_filter", label_visibility="collapsed",
    )
    selected_cat = shopping.CATEGORY_ORDER[cat_fi - 1] if cat_fi > 0 else None

    role_opts  = ["(alla roller)"] + [_ROLE_LABELS[r].split(" — ")[0] for r in _ROLE_IDS]
    role_fi    = col_role_filter.selectbox(
        "Roll", range(len(role_opts)),
        format_func=lambda i: role_opts[i],
        key="vh_role_filter", label_visibility="collapsed",
    )
    selected_role = _ROLE_IDS[role_fi - 1] if role_fi > 0 else None

    filtered = [
        item for item in all_items
        if (not search
            or search in item["name_sv"].lower()
            or any(search in s.lower() for s in item.get("synonyms", [])))
        and (selected_cat  is None or item.get("category") == selected_cat)
        and (selected_role is None or item.get("role")     == selected_role)
    ]

    total = len(filtered)
    st.caption(f"{total} varor visas av {len(all_items)}")

    if not filtered:
        st.info("Inga varor matchar filtret.")
        return

    # ── Paginering ────────────────────────────────────────────────────────────
    max_page = max(0, (total - 1) // _PAGE_SIZE)
    page = min(int(st.session_state.get("vh_page", 0)), max_page)

    page_items = filtered[page * _PAGE_SIZE:(page + 1) * _PAGE_SIZE]

    if max_page > 0:
        p_col, info_col, n_col = st.columns([1, 4, 1])
        if p_col.button("← Föregående", key="vh_prev", disabled=page == 0):
            st.session_state["vh_page"] = page - 1
            st.rerun()
        info_col.caption(f"Sida {page + 1} av {max_page + 1}  ({_PAGE_SIZE} per sida)")
        if n_col.button("Nästa →", key="vh_next", disabled=page == max_page):
            st.session_state["vh_page"] = page + 1
            st.rerun()

    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

    # ── Bekräftelsedialog (utanför loop för att undvika tung rendering) ───────
    confirm_key = "vh_confirm_delete"
    confirm_iid = st.session_state.get(confirm_key)

    if confirm_iid and confirm_iid in items_db:
        confirm_item = items_db[confirm_iid]
        uses = items_mod.find_recipe_uses(confirm_iid)
        if uses:
            st.error(
                f"**{confirm_item['name_sv']}** används i {len(uses)} recept: "
                f"{', '.join(uses)}. Redigera recepten innan du tar bort varan."
            )
            if st.button("Stäng", key="vh_close_error"):
                st.session_state.pop(confirm_key, None)
                st.rerun()
        else:
            st.warning(
                f"Ta bort **{confirm_item['name_sv']}** (`{confirm_iid}`)? Kan inte ångras."
            )
            yes_col, no_col, _ = st.columns([1, 1, 4])
            if yes_col.button("Ja, ta bort", key="vh_yes", type="primary"):
                items_mod.delete_item(confirm_iid)
                _invalidate_items_cache()
                st.session_state.pop(confirm_key, None)
                st.success(f"'{confirm_item['name_sv']}' borttagen.")
                st.rerun()
            if no_col.button("Avbryt", key="vh_no"):
                st.session_state.pop(confirm_key, None)
                st.rerun()

        st.markdown("<hr style='border-color:#D4DABC; margin:8px 0'>", unsafe_allow_html=True)

    # ── Varulista ─────────────────────────────────────────────────────────────
    for item in page_items:
        iid  = item["id"]
        cat  = CATEGORY_NAMES.get(item.get("category", ""), item.get("category", ""))
        role = _ROLE_LABELS.get(item.get("role", ""), item.get("role", "")).split(" — ")[0]

        col_name, col_cat, col_role, col_del = st.columns([4, 3, 3, 1])
        col_name.markdown(
            f"**{item['name_sv']}**  \n"
            f"<span style='font-size:0.75rem;color:#9A9A8A'>`{iid}`</span>",
            unsafe_allow_html=True,
        )
        col_cat.markdown(
            f"<span style='font-size:0.82rem;color:#7A7A6A'>{cat}</span>",
            unsafe_allow_html=True,
        )
        col_role.markdown(
            f"<span style='font-size:0.82rem;color:#7A7A6A'>{role}</span>",
            unsafe_allow_html=True,
        )
        if col_del.button("✕", key=f"vh_del_{iid}", help="Ta bort vara"):
            st.session_state[confirm_key] = iid
            st.rerun()


# ── Huvud-render ──────────────────────────────────────────────────────────────

def render() -> None:
    col_back, col_title = st.columns([1, 6])
    if col_back.button("← Tillbaka", key="vh_back"):
        st.session_state.pop("manage_items", None)
        st.session_state.pop("vh_page", None)
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
