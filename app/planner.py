"""AI-planering via Claude API — fritext-input → veckomenysförslag."""

import json
import os
from datetime import date, timedelta
from pathlib import Path

import anthropic
import yaml
from dotenv import dotenv_values

_env_path = Path(__file__).parent.parent / ".env"
_env = dotenv_values(_env_path)
os.environ.update({k: v for k, v in _env.items() if v is not None})

DATA_DIR    = Path(__file__).parent.parent / "data"
PLAN_PATH   = DATA_DIR / "weekly_plan.yaml"
RECIPES_DIR = DATA_DIR / "recipes"
PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


# ── Veckodatum-helpers ────────────────────────────────────────────────────────

def current_week_start() -> date:
    """Returnera måndagen i innevarande vecka."""
    today = date.today()
    return today - timedelta(days=today.weekday())


def week_start_for_offset(offset: int = 0) -> date:
    """Returnera måndagen för vecka +offset (0=denna, 1=nästa)."""
    return current_week_start() + timedelta(weeks=offset)


# ── Plan I/O ──────────────────────────────────────────────────────────────────

def load_plan() -> dict:
    """Ladda weekly_plan.yaml. Returnerar dict med week_start och meals."""
    if not PLAN_PATH.exists():
        return {"week_start": None, "meals": []}
    with open(PLAN_PATH, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return {
        "week_start":     data.get("week_start"),
        "meals":          list(data.get("meals") or []),
        "household_size": int(data.get("household_size") or 4),
    }


def save_plan(plan: dict) -> None:
    """Spara plan till weekly_plan.yaml."""
    with open(PLAN_PATH, "w", encoding="utf-8") as f:
        yaml.dump(plan, f, allow_unicode=True, sort_keys=False)


def clear_plan() -> None:
    """Nollställ veckoplanen."""
    save_plan({"week_start": None, "meals": []})


def is_plan_current(plan: dict) -> bool:
    """Returnera True om planen gäller innevarande vecka."""
    ws = plan.get("week_start")
    if not ws:
        return False
    if isinstance(ws, str):
        ws = date.fromisoformat(ws)
    return ws == current_week_start()


def _get_client() -> anthropic.Anthropic:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError(
            f"ANTHROPIC_API_KEY saknas. Kontrollera att .env finns i {_env_path.parent} "
            "och innehåller ANTHROPIC_API_KEY=din-nyckel"
        )
    return anthropic.Anthropic(api_key=api_key)


def _load_recipes() -> list[dict]:
    recipes = []
    for path in sorted(RECIPES_DIR.glob("*.yaml")):
        with open(path, encoding="utf-8") as f:
            recipes.append(yaml.safe_load(f))
    return recipes


def _recipe_summary(recipes: list[dict]) -> str:
    lines = []
    for r in recipes:
        tags = ", ".join(r.get("tags", []))
        meta = r.get("metadata", {})
        lines.append(
            f"- {r['recipe_id']}: {r['title']} "
            f"(tags: {tags}, tid: {meta.get('cook_time_minutes', '?')} min)"
        )
    return "\n".join(lines)


def _parse_json(raw: str) -> dict:
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1].rsplit("```", 1)[0]
    return json.loads(raw.strip())


def generate_weekly_plan(user_input: str, days: list[str]) -> dict:
    """Ta fritext-input och valda dagar, returnera ett veckomenysförslag som dict."""
    recipes = _load_recipes()
    prompt_template = (PROMPTS_DIR / "weekly_planner.txt").read_text(encoding="utf-8")
    prompt = prompt_template.format(
        user_input=user_input,
        recipes=_recipe_summary(recipes),
        days=", ".join(days),
    )
    message = _get_client().messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    return _parse_json(message.content[0].text)


def suggest_replacement(day: str, current_plan: dict) -> dict:
    """Föreslå en ersättningsrätt för en specifik dag."""
    recipes = _load_recipes()
    current_ids = {m["recipe_id"] for m in current_plan.get("meals", [])}
    available = [r for r in recipes if r["recipe_id"] not in current_ids] or recipes

    prompt = (
        f"Föreslå EN middagsrätt för {day} som ersättning i veckomenyn.\n\n"
        f"Tillgängliga recept:\n{_recipe_summary(available)}\n\n"
        f"Returnera ENDAST giltig JSON utan förklarande text:\n"
        f'{{ "day": "{day}", "recipe_id": "...", "title": "..." }}'
    )
    message = _get_client().messages.create(
        model="claude-sonnet-4-6",
        max_tokens=256,
        messages=[{"role": "user", "content": prompt}],
    )
    return _parse_json(message.content[0].text)
