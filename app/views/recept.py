"""Receptvisare och URL-import — mobilanpassad."""

from pathlib import Path

import streamlit as st
import yaml

from app.recipes import load_all_recipes, load_recipe, save_recipe, delete_recipe
from app import shopping, importer
from app.planner import current_week_start, week_start_for_offset, load_plan

PLAN_PATH = Path(__file__).parent.parent.parent / "data" / "weekly_plan.yaml"

_NO_LINK = "(ingen koppling)"


def _week_recipe_ids(offset: int) -> set[str]:
    """Returnera recipe_id:n för den vecka som är offset veckor från nu."""
    plan = load_plan()
    ws = plan.get("week_start")
    if isinstance(ws, str):
        from datetime import date
        ws = date.fromisoformat(ws)
    target = week_start_for_offset(offset)
    if ws == target and plan.get("meals"):
        return {m["recipe_id"] for m in plan["meals"]}
    return set()


def _clear_import():
    for key in ("import_recipe", "import_matches", "import_url"):
        st.session_state.pop(key, None)
    # Rensa selectbox-nycklar
    for k in list(st.session_state.keys()):
        if k.startswith("ing_sel_"):
            del st.session_state[k]


def _render_import(items_db: dict):
    """Importflöde: URL → extraktion → granskning → spara."""

    has_pending = bool(st.session_state.get("import_recipe"))

    with st.expander("➕ Importera recept från URL", expanded=has_pending):

        # ── Steg 1: URL-inmatning ──────────────────────────────────────────
        if not has_pending:
            url = st.text_input(
                "Receptlänk",
                placeholder="https://www.koket.se/...",
                label_visibility="collapsed",
            )
            if st.button("Hämta recept", use_container_width=True):
                if not url.strip():
                    st.warning("Klistra in en URL först.")
                else:
                    with st.spinner("Hämtar och analyserar receptet…"):
                        try:
                            html = importer.fetch_url(url.strip())
                            raw = importer.extract_recipe(html, url.strip())
                            matches = importer.match_ingredients(
                                raw["ingredients"], items_db
                            )
                            st.session_state.import_recipe = raw
                            st.session_state.import_matches = matches
                            st.session_state.import_url = url.strip()
                        except Exception as e:
                            st.error(f"Kunde inte hämta receptet: {e}")
                    st.rerun()
            return

        # ── Steg 2: Granska och godkänn ───────────────────────────────────
        raw = st.session_state.import_recipe
        matches = st.session_state.import_matches
        url = st.session_state.import_url

        meta = (
            f"{raw.get('servings', '?')} port · "
            f"{raw.get('cook_time_minutes', '?')} min · "
            f"Svårighet {raw.get('difficulty', '?')}/3"
        )
        st.markdown(
            f"<div style='line-height:1.1;padding-bottom:2px;font-size:1rem;font-weight:700;color:#2A2A22'>{raw['title']}</div>"
            f"<div style='line-height:1.3;padding-bottom:6px;font-size:0.8rem;color:#7A7A6A'>{meta}</div>"
            f"<div style='line-height:1.3;font-size:0.88rem;font-weight:700;color:#2A2A22'>Ingredienser</div>"
            f"<div style='height:21px'></div>",
            unsafe_allow_html=True,
        )

        # Svenska namn i selectboxen: {name_sv → item_id}
        sv_to_id = {item["name_sv"]: iid for iid, item in items_db.items()}
        sv_options = [_NO_LINK] + sorted(sv_to_id.keys())

        unmatched_count = sum(1 for m in matches if not m["matched_id"])
        if unmatched_count:
            st.markdown(
                f"<div style='line-height:1.3;font-size:0.8rem;color:#7A7A6A'>"
                f"{unmatched_count} ingrediens(er) utan koppling — välj vara i höger kolumn.</div>"
                f"<div style='height:24px'></div>",
                unsafe_allow_html=True,
            )

        for i, m in enumerate(matches):
            amt = m.get("amount") or 0
            try:
                amt_f = float(amt)
            except (TypeError, ValueError):
                amt_f = 0.0
            unit = (m.get("unit") or "").strip()
            if amt_f > 0 and unit:
                amt_val = int(amt_f) if amt_f == int(amt_f) else amt_f
                amt_str = f"{amt_val} {unit}"
            else:
                amt_str = ""

            col1, col2 = st.columns([5, 4])

            if m["matched_id"]:
                # Matchad — visa namn (+ mängd om känd), selectbox förvald
                matched_sv = items_db[m["matched_id"]]["name_sv"]
                qty_part = f" — <em>{amt_str}</em>" if amt_str else ""
                col1.markdown(
                    f"<p style='margin:0;padding:3px 0;font-size:0.88rem;color:#2A2A22'>"
                    f"✓ {m['name']}{qty_part}</p>",
                    unsafe_allow_html=True,
                )
                default_idx = sv_options.index(matched_sv) if matched_sv in sv_options else 0
                col2.selectbox(
                    "",
                    sv_options,
                    index=default_idx,
                    key=f"ing_sel_{i}",
                    label_visibility="collapsed",
                )
            else:
                # Omatchad — redigerbart namnfält + selectbox
                col1.text_input(
                    "",
                    value=m["name"],
                    key=f"ing_name_{i}",
                    label_visibility="collapsed",
                )
                col2.selectbox(
                    "",
                    sv_options,
                    index=0,
                    key=f"ing_sel_{i}",
                    label_visibility="collapsed",
                )

        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

        col_save, col_cancel = st.columns(2)
        if col_save.button("✓ Spara recept", use_container_width=True):
            # Reverse-lookup: svenska namn → item_id; respektera alla overrides
            overrides = {}
            for i in range(len(matches)):
                sel = st.session_state.get(f"ing_sel_{i}")
                if sel and sel != _NO_LINK:
                    iid = sv_to_id.get(sel)
                    if iid:
                        overrides[i] = iid
                elif not m["matched_id"]:
                    # Spara det redigerade namnet som ID-slug om ingen koppling vald
                    edited = st.session_state.get(f"ing_name_{i}", matches[i]["name"])
                    matches[i] = {**matches[i], "name": edited}
            recipe_dict = importer.build_recipe_dict(raw, matches, overrides, url)
            save_recipe(recipe_dict)
            st.success(f"Receptet '{recipe_dict['title']}' sparat!")
            _clear_import()
            st.rerun()

        if col_cancel.button("✕ Avbryt", use_container_width=True):
            _clear_import()
            st.rerun()


def render():
    st.title("Recept")

    items_db = shopping.load_items()
    _render_import(items_db)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ── Filterläge ────────────────────────────────────────────────────────
    filter_mode = st.radio(
        "Visa",
        options=["alla", "denna_vecka", "nasta_vecka"],
        format_func=lambda x: {
            "alla":        "Alla recept",
            "denna_vecka": "Denna vecka",
            "nasta_vecka": "Nästa vecka",
        }[x],
        horizontal=True,
        key="recipe_filter",
        label_visibility="collapsed",
    )

    all_recipes = load_all_recipes()
    search_str = ""

    if filter_mode == "alla":
        search_str = st.text_input(
            "Sök recept",
            placeholder="Filtrera recept…",
            label_visibility="collapsed",
            key="recipe_search",
        ).strip().lower()
        filtered = (
            [r for r in all_recipes if search_str in r["title"].lower()]
            if search_str else all_recipes
        )
    else:
        offset = 0 if filter_mode == "denna_vecka" else 1
        ids = _week_recipe_ids(offset)
        filtered = [r for r in all_recipes if r["recipe_id"] in ids]

    if not filtered:
        if filter_mode == "alla":
            st.info(f"Inga recept matchar '{search_str}'." if search_str else "Inga recept finns.")
        else:
            label = "denna vecka" if filter_mode == "denna_vecka" else "nästa vecka"
            st.info(f"Ingen meny planerad för {label}.")
        return

    recipe_options = {r["title"]: r["recipe_id"] for r in filtered}

    selected_title = st.selectbox(
        "Välj recept",
        list(recipe_options.keys()),
        label_visibility="collapsed",
        key="recipe_select",
    )
    recipe = load_recipe(recipe_options[selected_title])
    if not recipe:
        st.error("Kunde inte ladda receptet.")
        return

    # ── Receptdetaljer ────────────────────────────────────────────────────
    meta = recipe.get("metadata", {})

    st.header(recipe["title"])

    col1, col2, col3 = st.columns(3)
    col1.metric("Portioner", recipe.get("servings", "?"))
    col2.metric("Tid", f"{meta.get('cook_time_minutes', '?')} min")
    col3.metric("Svårighetsgrad", f"{meta.get('difficulty', '?')}/3")

    st.subheader("Ingredienser")
    for ing in recipe.get("ingredients", []):
        item = items_db.get(ing["ingredient_id"])
        name = item["name_sv"] if item else ing["ingredient_id"].replace("_", " ")
        try:
            amt_f = float(ing.get("amount") or 0)
            amt_val = int(amt_f) if amt_f == int(amt_f) else amt_f
            amt_str = f"{amt_val} {ing['unit']}" if amt_f > 0 else ""
        except (TypeError, ValueError):
            amt_str = ""
        suffix = f" — **{amt_str}**" if amt_str else ""
        st.markdown(f"- {name}{suffix}")

    st.subheader("Tillagning")
    steps_html = "".join(
        f"<p style='padding-left:1.6em; text-indent:-1.6em; margin:0 0 7px 0; "
        f"line-height:1.35; font-size:0.9rem; color:#2A2A22'>"
        f"<strong style='color:#2A2A22'>{s['step']}.</strong> {s['text']}</p>"
        for s in recipe.get("instructions", [])
    )
    st.markdown(steps_html, unsafe_allow_html=True)

    if recipe.get("tags"):
        tags_str = " · ".join(recipe["tags"])
        st.markdown(
            f"<div style='height:10px'></div>"
            f"<hr style='border-color:#D4DABC; margin:0 0 8px 0'>"
            f"<div style='font-size:0.8rem; color:#AAAAAA; margin:0; "
            f"visibility:visible; opacity:1'>{tags_str}</div>",
            unsafe_allow_html=True,
        )

    if meta.get("source_url"):
        st.markdown(
            f"<div style='font-size:0.75rem; color:#AAAAAA; margin-top:4px'>"
            f"Källa: {meta['source_url']}</div>",
            unsafe_allow_html=True,
        )

    # ── Ta bort recept ────────────────────────────────────────────────────
    st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)
    st.divider()
    recipe_id = recipe["recipe_id"]

    if st.session_state.get("confirm_delete") == recipe_id:
        st.warning(f"Ta bort **{recipe['title']}**? Detta kan inte ångras.")
        yes_col, no_col = st.columns(2)
        if yes_col.button("Ja, ta bort", use_container_width=True):
            delete_recipe(recipe_id)
            st.session_state.pop("confirm_delete", None)
            st.session_state.pop("recipe_select", None)
            st.rerun()
        if no_col.button("Avbryt", use_container_width=True):
            st.session_state.pop("confirm_delete", None)
            st.rerun()
    else:
        if st.button("Ta bort recept", use_container_width=True):
            st.session_state["confirm_delete"] = recipe_id
            st.rerun()
