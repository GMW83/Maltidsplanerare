"""Receptvisare, URL-import och redigering — mobilanpassad visning, desktop-redigering."""

from pathlib import Path

import streamlit as st

from app.recipes import load_all_recipes, load_recipe, save_recipe, delete_recipe
from app import shopping, importer
from app.planner import current_week_start, week_start_for_offset, load_plan
from app.utils import is_mobile as _is_mobile

PLAN_PATH = Path(__file__).parent.parent.parent / "data" / "weekly_plan.yaml"

_NO_LINK = "(ingen koppling)"


def _week_plan_info(offset: int) -> tuple[set[str], int]:
    """Returnera (recipe_ids, household_size) för vecka +offset."""
    plan = load_plan()
    ws = plan.get("week_start")
    if isinstance(ws, str):
        from datetime import date
        ws = date.fromisoformat(ws)
    target = week_start_for_offset(offset)
    if ws == target and plan.get("meals"):
        ids = {m["recipe_id"] for m in plan["meals"]}
        return ids, plan.get("household_size", 4)
    return set(), 4


# ── Import ────────────────────────────────────────────────────────────────────

def _clear_import():
    for key in ("import_recipe", "import_matches", "import_url"):
        st.session_state.pop(key, None)
    for k in list(st.session_state.keys()):
        if k.startswith("ing_sel_") or k.startswith("ing_name_"):
            del st.session_state[k]


def _render_import(items_db: dict):
    has_pending = bool(st.session_state.get("import_recipe"))

    with st.expander("➕ Importera recept från URL", expanded=has_pending):

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
                            matches = importer.match_ingredients(raw["ingredients"], items_db)
                            st.session_state.import_recipe = raw
                            st.session_state.import_matches = matches
                            st.session_state.import_url = url.strip()
                        except Exception as e:
                            st.error(f"Kunde inte hämta receptet: {e}")
                    st.rerun()
            return

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
                matched_sv = items_db[m["matched_id"]]["name_sv"]
                qty_part = f" — <em>{amt_str}</em>" if amt_str else ""
                col1.markdown(
                    f"<p style='margin:0;padding:3px 0;font-size:0.88rem;color:#2A2A22'>"
                    f"✓ {m['name']}{qty_part}</p>",
                    unsafe_allow_html=True,
                )
                default_idx = sv_options.index(matched_sv) if matched_sv in sv_options else 0
                col2.selectbox("", sv_options, index=default_idx, key=f"ing_sel_{i}", label_visibility="collapsed")
            else:
                col1.text_input("", value=m["name"], key=f"ing_name_{i}", label_visibility="collapsed")
                col2.selectbox("", sv_options, index=0, key=f"ing_sel_{i}", label_visibility="collapsed")

        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

        col_save, col_cancel = st.columns(2)
        if col_save.button("✓ Spara recept", use_container_width=True):
            overrides = {}
            for i in range(len(matches)):
                sel = st.session_state.get(f"ing_sel_{i}")
                if sel and sel != _NO_LINK:
                    iid = sv_to_id.get(sel)
                    if iid:
                        overrides[i] = iid
                elif not m["matched_id"]:
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


# ── Redigering ────────────────────────────────────────────────────────────────

def _clear_edit_state():
    for key in ["_edit_recipe_id", "edit_title", "edit_servings", "edit_cook_time",
                "edit_difficulty", "edit_tags", "edit_ingredients", "edit_steps"]:
        st.session_state.pop(key, None)
    for k in list(st.session_state.keys()):
        if k.startswith("ei_"):
            del st.session_state[k]


def _init_edit_state(recipe: dict):
    if st.session_state.get("_edit_recipe_id") == recipe["recipe_id"]:
        return
    meta = recipe.get("metadata", {})
    st.session_state["_edit_recipe_id"] = recipe["recipe_id"]
    st.session_state["edit_title"] = recipe["title"]
    st.session_state["edit_servings"] = int(recipe.get("servings", 4))
    st.session_state["edit_cook_time"] = int(meta.get("cook_time_minutes", 30))
    st.session_state["edit_difficulty"] = int(meta.get("difficulty", 2))
    st.session_state["edit_tags"] = ", ".join(recipe.get("tags", []))
    st.session_state["edit_ingredients"] = [
        {
            "ingredient_id": ing["ingredient_id"],
            "amount": float(ing.get("amount") or 0),
            "unit": str(ing.get("unit") or ""),
            "display_name": ing.get("display_name"),
        }
        for ing in recipe.get("ingredients", [])
    ]
    st.session_state["edit_steps"] = [
        {"text": s.get("text", "")}
        for s in recipe.get("instructions", [])
    ]


def _sync_widgets_to_lists(items_db: dict):
    """Samla in widgetvärden i listorna och rensa widget-nycklar."""
    sv_to_id = {item["name_sv"]: iid for iid, item in items_db.items()}

    ings = st.session_state.get("edit_ingredients", [])
    for i in range(len(ings)):
        sel = st.session_state.get(f"ei_ing_sel_{i}")
        if sel is not None:
            ings[i]["ingredient_id"] = sv_to_id.get(sel, ings[i]["ingredient_id"])
        amt = st.session_state.get(f"ei_ing_amt_{i}")
        if amt is not None:
            ings[i]["amount"] = float(amt)
        unit = st.session_state.get(f"ei_ing_unit_{i}")
        if unit is not None:
            ings[i]["unit"] = unit

    steps = st.session_state.get("edit_steps", [])
    for i in range(len(steps)):
        text = st.session_state.get(f"ei_step_{i}")
        if text is not None:
            steps[i]["text"] = text

    for k in list(st.session_state.keys()):
        if k.startswith("ei_ing_") or k.startswith("ei_step_"):
            del st.session_state[k]


def _render_edit(recipe: dict, items_db: dict):
    _init_edit_state(recipe)

    st.subheader("Redigera recept")

    # ── Metadata ──────────────────────────────────────────────────────────────
    st.text_input("Titel", key="edit_title")
    col1, col2, col3 = st.columns(3)
    col1.number_input("Portioner", min_value=1, max_value=20, step=1, key="edit_servings")
    col2.number_input("Tid (min)", min_value=1, max_value=480, step=5, key="edit_cook_time")
    col3.number_input("Svårighet (1–3)", min_value=1, max_value=3, step=1, key="edit_difficulty")

    # ── Ingredienser ──────────────────────────────────────────────────────────
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.subheader("Ingredienser")

    sv_to_id = {item["name_sv"]: iid for iid, item in items_db.items()}
    id_to_sv = {v: k for k, v in sv_to_id.items()}
    sv_options = sorted(sv_to_id.keys())

    ings = st.session_state["edit_ingredients"]
    ing_to_delete = None

    for i, ing in enumerate(ings):
        current_name = id_to_sv.get(ing["ingredient_id"]) or ing.get("display_name") or ing["ingredient_id"].replace("_", " ")
        if current_name in sv_options:
            options = sv_options
            default_idx = sv_options.index(current_name)
        else:
            options = [current_name] + sv_options
            default_idx = 0

        col_ing, col_amt, col_unit, col_del = st.columns([5, 2, 2, 1])
        col_ing.selectbox("", options, index=default_idx, key=f"ei_ing_sel_{i}", label_visibility="collapsed")
        col_amt.number_input("", value=ing["amount"], min_value=0.0, step=0.5, key=f"ei_ing_amt_{i}", label_visibility="collapsed")
        col_unit.text_input("", value=ing["unit"], key=f"ei_ing_unit_{i}", label_visibility="collapsed")
        if col_del.button("✕", key=f"ei_ing_del_{i}", use_container_width=True):
            ing_to_delete = i

    if ing_to_delete is not None:
        _sync_widgets_to_lists(items_db)
        st.session_state["edit_ingredients"].pop(ing_to_delete)
        st.rerun()

    if st.button("+ Lägg till ingrediens", key="ei_add_ing"):
        _sync_widgets_to_lists(items_db)
        first_id = next(iter(sv_to_id.values())) if sv_to_id else ""
        st.session_state["edit_ingredients"].append({"ingredient_id": first_id, "amount": 0.0, "unit": "g"})
        st.rerun()

    # ── Tillagning ────────────────────────────────────────────────────────────
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.subheader("Tillagning")

    steps = st.session_state["edit_steps"]
    step_to_delete = None

    for i, step in enumerate(steps):
        hdr_col, del_col = st.columns([10, 1])
        hdr_col.markdown(f"**Steg {i + 1}**")
        if del_col.button("✕", key=f"ei_step_del_{i}", use_container_width=True):
            step_to_delete = i
        st.text_area("", value=step["text"], key=f"ei_step_{i}", label_visibility="collapsed", height=80)

    if step_to_delete is not None:
        _sync_widgets_to_lists(items_db)
        st.session_state["edit_steps"].pop(step_to_delete)
        st.rerun()

    if st.button("+ Lägg till steg", key="ei_add_step"):
        _sync_widgets_to_lists(items_db)
        st.session_state["edit_steps"].append({"text": ""})
        st.rerun()

    # ── Taggar ────────────────────────────────────────────────────────────────
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.text_input("Taggar (kommaseparerade)", key="edit_tags")

    # ── Spara / Avbryt ────────────────────────────────────────────────────────
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    save_col, cancel_col = st.columns(2)

    if save_col.button("✓ Spara recept", use_container_width=True, type="primary"):
        _sync_widgets_to_lists(items_db)
        updated = {
            "recipe_id": recipe["recipe_id"],
            "title": st.session_state["edit_title"].strip(),
            "servings": int(st.session_state["edit_servings"]),
            "ingredients": [
                {
                    "ingredient_id": ing["ingredient_id"],
                    "amount": ing["amount"],
                    "unit": ing["unit"],
                    **({"display_name": ing["display_name"]} if ing.get("display_name") else {}),
                }
                for ing in st.session_state["edit_ingredients"]
            ],
            "instructions": [
                {"step": i + 1, "text": s["text"].strip()}
                for i, s in enumerate(st.session_state["edit_steps"])
                if s["text"].strip()
            ],
            "tags": [t.strip() for t in st.session_state["edit_tags"].split(",") if t.strip()],
            "metadata": {
                "cook_time_minutes": int(st.session_state["edit_cook_time"]),
                "difficulty": int(st.session_state["edit_difficulty"]),
                "source_url": recipe.get("metadata", {}).get("source_url", ""),
            },
        }
        save_recipe(updated)
        st.session_state.pop("edit_mode", None)
        _clear_edit_state()
        st.success(f"'{updated['title']}' sparat!")
        st.rerun()

    if cancel_col.button("✕ Avbryt", use_container_width=True):
        st.session_state.pop("edit_mode", None)
        _clear_edit_state()
        st.rerun()


# ── Huvudvy ───────────────────────────────────────────────────────────────────

def render():
    st.title("Recept")

    items_db = shopping.load_items()
    _render_import(items_db)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ── Filterläge ────────────────────────────────────────────────────────────
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
    week_household_size = None

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
        ids, week_household_size = _week_plan_info(offset)
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

    # ── Redigeringsläge (desktop only) ────────────────────────────────────────
    if st.session_state.get("edit_mode") == recipe["recipe_id"]:
        _render_edit(recipe, items_db)
        return

    # ── Läsvy ─────────────────────────────────────────────────────────────────
    meta = recipe.get("metadata", {})

    st.header(recipe["title"])

    orig_servings = recipe.get("servings") or 4
    if week_household_size and week_household_size != orig_servings:
        scale = week_household_size / orig_servings
        col1, col2, col3 = st.columns(3)
        col1.metric("Portioner", week_household_size,
                    delta=f"originalet {orig_servings} port",
                    delta_color="off")
        col2.metric("Tid", f"{meta.get('cook_time_minutes', '?')} min")
        col3.metric("Svårighetsgrad", f"{meta.get('difficulty', '?')}/3")
    else:
        scale = 1.0
        col1, col2, col3 = st.columns(3)
        col1.metric("Portioner", orig_servings)
        col2.metric("Tid", f"{meta.get('cook_time_minutes', '?')} min")
        col3.metric("Svårighetsgrad", f"{meta.get('difficulty', '?')}/3")

    st.subheader("Ingredienser")
    for ing in recipe.get("ingredients", []):
        item = items_db.get(ing["ingredient_id"])
        name = item["name_sv"] if item else (ing.get("display_name") or ing["ingredient_id"].replace("_", " "))
        try:
            amt_f = float(ing.get("amount") or 0) * scale
            amt_val = int(amt_f) if amt_f == int(amt_f) else round(amt_f, 1)
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

    bottom = [
        "<div style='height:10px'></div>",
        "<hr style='border-color:#D4DABC; margin:0'>",
    ]
    if recipe.get("tags"):
        tags_str = " · ".join(recipe["tags"])
        bottom.append(
            f"<div style='font-size:0.8rem; color:#AAAAAA; margin:0; "
            f"visibility:visible; opacity:1'>{tags_str}</div>"
        )
    if meta.get("source_url"):
        bottom.append(
            f"<div style='font-size:0.75rem; color:#AAAAAA; margin-top:0'>"
            f"Källa: {meta['source_url']}</div>"
        )
    bottom.append("<div style='height:20px'></div>")
    st.markdown("".join(bottom), unsafe_allow_html=True)

    # ── Knappar: Redigera och Ta bort (desktop only) ──────────────────────────
    recipe_id = recipe["recipe_id"]

    if not _is_mobile():
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
            edit_col, del_col = st.columns(2)
            if edit_col.button("Redigera recept", use_container_width=True):
                st.session_state["edit_mode"] = recipe_id
                _clear_edit_state()
                st.rerun()
            if del_col.button("Ta bort recept", use_container_width=True):
                st.session_state["confirm_delete"] = recipe_id
                st.rerun()
    else:
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
