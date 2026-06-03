"""Varuhantering — lägg till och ta bort varor i varudatabasen (desktop only)."""

import streamlit as st

from app import items as items_mod, shopping, store_profiles

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
    for k in list(st.session_state.keys()):
        if k.startswith("il_cat_") or k.startswith("il_role_"):
            del st.session_state[k]


def _make_cat_saver(item: dict, cat_ids: list) -> callable:
    def _save():
        new_cat = cat_ids[st.session_state[f"il_cat_{item['id']}"]]
        pid = store_profiles.active_id()
        if new_cat.startswith("custom_"):
            # Profilegen kategori — spara som override, ändra inte items.yaml
            store_profiles.set_item_override(pid, item["id"], new_cat)
        else:
            # Global kategori — uppdatera items.yaml och ta bort eventuell override
            items_mod.update_item(
                item_id=item["id"],
                name_sv=item["name_sv"],
                category=new_cat,
                unit=item.get("unit", "g"),
                role=item.get("role", "ingredient"),
                synonyms=item.get("synonyms"),
            )
            store_profiles.set_item_override(pid, item["id"], None)
        _invalidate_items_cache()
    return _save


def _make_role_saver(item: dict) -> callable:
    def _save():
        new_role = _ROLE_IDS[st.session_state[f"il_role_{item['id']}"]]
        items_mod.update_item(
            item_id=item["id"],
            name_sv=item["name_sv"],
            category=item.get("category", "ovrigt"),
            unit=item.get("unit", "g"),
            role=new_role,
            synonyms=item.get("synonyms"),
        )
        _invalidate_items_cache()
    return _save


def _load_item_into_form(item: dict) -> None:
    """Ladda en befintlig varas värden i formulärfälten och sätt edit-läge."""
    cat_ids = list(CATEGORY_NAMES.keys())
    cat = item.get("category", cat_ids[0])
    unit = item.get("unit", "g")
    role = item.get("role", "ingredient")

    st.session_state["vh_edit_id"]  = item["id"]
    st.session_state["vh_name"]     = item["name_sv"]
    st.session_state["vh_cat"]      = cat_ids.index(cat) if cat in cat_ids else 0
    st.session_state["vh_unit"]     = _UNITS.index(unit) if unit in _UNITS else 0
    st.session_state["vh_role"]     = _ROLE_IDS.index(role) if role in _ROLE_IDS else 0
    st.session_state["vh_synonyms"] = ", ".join(item.get("synonyms", []))


def _clear_form() -> None:
    st.session_state["vh_pending_clear"] = True
    st.session_state.pop("vh_edit_id", None)


# ── Formulär (lägg till / redigera) ──────────────────────────────────────────

def _render_form() -> None:
    edit_id   = st.session_state.get("vh_edit_id")
    edit_mode = bool(edit_id)

    if edit_mode:
        items_db = shopping.load_items()
        edit_item = items_db.get(edit_id, {})
        st.subheader(f"Redigera: {edit_item.get('name_sv', edit_id)}")
        st.caption(f"ID: `{edit_id}` (kan inte ändras)")
    else:
        st.subheader("Lägg till vara")

    name = st.text_input("Namn (svenska)", key="vh_name", placeholder="t.ex. havregryn")

    if not edit_mode:
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

    if edit_mode:
        save_col, cancel_col = st.columns(2)
        if save_col.button("Spara ändringar", type="primary", key="vh_save_btn", use_container_width=True):
            if not name.strip():
                st.warning("Ange ett namn.")
                return
            if items_mod.name_exists_excluding(name, edit_id):
                st.error(f"En annan vara med namnet '{name.strip()}' finns redan.")
                return
            synonyms = [s for s in synonyms_raw.split(",") if s.strip()] if synonyms_raw else []
            items_mod.update_item(
                item_id=edit_id,
                name_sv=name.strip(),
                category=cat_ids[cat_idx],
                unit=unit,
                role=_ROLE_IDS[role_idx],
                synonyms=synonyms,
            )
            _invalidate_items_cache()
            st.success(f"'{name.strip()}' uppdaterad.")
            _clear_form()
            st.rerun()
        if cancel_col.button("Avbryt", key="vh_cancel_edit", use_container_width=True):
            _clear_form()
            st.rerun()
    else:
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

    col_search, col_cat_filter, col_role_filter = st.columns([3, 2, 2])
    search = col_search.text_input(
        "Sök", placeholder="Filtrera på namn…",
        key="vh_search", label_visibility="collapsed",
    ).strip().lower()

    all_cats = ["(alla kategorier)"] + [CATEGORY_NAMES.get(c, c) for c in shopping.CATEGORY_ORDER]
    cat_fi   = col_cat_filter.selectbox(
        "Kategori", range(len(all_cats)),
        format_func=lambda i: all_cats[i],
        key="vh_cat_filter", label_visibility="collapsed",
    )
    selected_cat = shopping.CATEGORY_ORDER[cat_fi - 1] if cat_fi > 0 else None

    role_opts = ["(alla roller)"] + [_ROLE_LABELS[r].split(" — ")[0] for r in _ROLE_IDS]
    role_fi   = col_role_filter.selectbox(
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
    max_page  = max(0, (total - 1) // _PAGE_SIZE)
    page      = min(int(st.session_state.get("vh_page", 0)), max_page)
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

    # ── Bekräftelsedialog för borttagning (utanför loop) ─────────────────────
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
            st.warning(f"Ta bort **{confirm_item['name_sv']}** (`{confirm_iid}`)? Kan inte ångras.")
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
    current_edit_id = st.session_state.get("vh_edit_id")

    # Bygg kombinerad kategorilista: globala + aktiv profils egna kategorier
    global_cat_ids = list(CATEGORY_NAMES.keys())
    active_profile = store_profiles.active()
    profile_cat_names = active_profile.get("category_names", {})
    profile_overrides = active_profile.get("item_overrides", {})

    all_cat_ids   = global_cat_ids[:]
    all_cat_names = dict(CATEGORY_NAMES)
    for cat_id, cat_name in profile_cat_names.items():
        if cat_id not in all_cat_names:
            all_cat_ids.append(cat_id)
            all_cat_names[cat_id] = cat_name

    for item in page_items:
        iid = item["id"]

        # Visa profilens override om den finns, annars varans egna kategori
        effective_cat = profile_overrides.get(iid) or item.get("category", all_cat_ids[0])
        cat_idx       = all_cat_ids.index(effective_cat) if effective_cat in all_cat_ids else 0
        current_role  = item.get("role", _ROLE_IDS[0])
        role_idx      = _ROLE_IDS.index(current_role) if current_role in _ROLE_IDS else 0

        col_name, col_cat, col_role, col_edit, col_del = st.columns([3, 3, 3, 1, 1])
        col_name.markdown(
            f"**{item['name_sv']}**  \n"
            f"<span style='font-size:0.75rem;color:#9A9A8A'>`{iid}`</span>",
            unsafe_allow_html=True,
        )
        col_cat.selectbox(
            "",
            options=range(len(all_cat_ids)),
            format_func=lambda i: all_cat_names[all_cat_ids[i]],
            index=cat_idx,
            key=f"il_cat_{iid}",
            on_change=_make_cat_saver(item, all_cat_ids),
            label_visibility="collapsed",
        )
        col_role.selectbox(
            "",
            options=range(len(_ROLE_IDS)),
            format_func=lambda i: _ROLE_LABELS[_ROLE_IDS[i]].split(" — ")[0],
            index=role_idx,
            key=f"il_role_{iid}",
            on_change=_make_role_saver(item),
            label_visibility="collapsed",
        )
        if col_edit.button(
            "✎", key=f"vh_edit_{iid}",
            help="Redigera vara",
            type="primary" if iid == current_edit_id else "secondary",
        ):
            # Sätt pending-nyckel — widget-nycklarna sätts i render() innan
            # formuläret renderas, annars klagar Streamlit på låsta nycklar
            st.session_state["vh_pending_edit_id"] = iid
            st.session_state.pop(confirm_key, None)
            st.rerun()
        if col_del.button("✕", key=f"vh_del_{iid}", help="Ta bort vara"):
            st.session_state[confirm_key] = iid
            st.session_state.pop("vh_edit_id", None)
            st.rerun()


# ── Huvud-render ──────────────────────────────────────────────────────────────

def render() -> None:
    # Hantera pending edit-begäran INNAN några widgets skapas —
    # Streamlit tillåter inte att widget-nycklar skrivs efter att widgeten renderats
    pending = st.session_state.pop("vh_pending_edit_id", None)
    if pending:
        items_db_now = shopping.load_items()
        if pending in items_db_now:
            _load_item_into_form(items_db_now[pending])

    if st.session_state.pop("vh_pending_clear", False):
        st.session_state["vh_name"]     = ""
        st.session_state["vh_synonyms"] = ""
        st.session_state["vh_cat"]      = 0
        st.session_state["vh_unit"]     = 0
        st.session_state["vh_role"]     = 0

    col_back, col_title = st.columns([1, 6])
    if col_back.button("← Tillbaka", key="vh_back"):
        st.session_state.pop("manage_items", None)
        st.session_state.pop("vh_page", None)
        _clear_form()
        st.rerun()
    col_title.markdown("## Varuhantering")

    st.markdown(
        "<hr style='border-color:#D4DABC; margin:4px 0 16px 0'>",
        unsafe_allow_html=True,
    )

    _render_form()

    st.markdown(
        "<hr style='border-color:#D4DABC; margin:16px 0'>",
        unsafe_allow_html=True,
    )

    _render_item_list()
