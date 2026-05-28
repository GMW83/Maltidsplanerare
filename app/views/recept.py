"""Receptvisare och URL-import — mobilanpassad."""

from pathlib import Path

import streamlit as st
import yaml

from app.recipes import load_all_recipes, load_recipe, save_recipe
from app import shopping, importer

PLAN_PATH = Path(__file__).parent.parent.parent / "data" / "weekly_plan.yaml"

_NO_LINK = "(ingen koppling)"


def _load_plan() -> dict:
    if PLAN_PATH.exists():
        with open(PLAN_PATH, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}


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
            f"<div style='height:6px'></div>",
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
                f"<div style='height:10px'></div>",
                unsafe_allow_html=True,
            )

        for i, m in enumerate(matches):
            amt = m["amount"]
            amt_str = f"{int(amt) if isinstance(amt, float) and amt == int(amt) else amt} {m['unit']}"

            col1, col2 = st.columns([5, 4])

            if m["matched_id"]:
                # Matchad — visa namn + mängd, selectbox förvald (kan ändras)
                matched_sv = items_db[m["matched_id"]]["name_sv"]
                col1.markdown(
                    f"<p style='margin:0;padding:3px 0;font-size:0.88rem;color:#2A2A22'>"
                    f"✓ {m['name']} — <em>{amt_str}</em></p>",
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

    # ── Receptvisare ──────────────────────────────────────────────────────
    plan = _load_plan()

    if plan.get("meals"):
        recipe_options = {m["title"]: m["recipe_id"] for m in plan["meals"]}
        st.caption("Veckans recept")
    else:
        all_recipes = load_all_recipes()
        recipe_options = {r["title"]: r["recipe_id"] for r in all_recipes}
        st.caption("Alla recept")

    if not recipe_options:
        st.info("Inga recept tillgängliga.")
        return

    selected = st.selectbox(
        "Välj recept",
        list(recipe_options.keys()),
        label_visibility="collapsed",
    )
    recipe = load_recipe(recipe_options[selected])
    if not recipe:
        st.error("Kunde inte ladda receptet.")
        return

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
        amt = ing["amount"]
        amt_str = f"{int(amt) if float(amt) == int(amt) else amt} {ing['unit']}"
        st.markdown(f"- {name} — **{amt_str}**")

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
