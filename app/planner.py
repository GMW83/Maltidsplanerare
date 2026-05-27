"""AI-planering via Claude API — fritext-input → veckomenysförslag."""

import json
import os
from pathlib import Path

import anthropic
import yaml
from dotenv import dotenv_values

_env_path = Path(__file__).parent.parent / ".env"
_env = dotenv_values(_env_path)
os.environ.update({k: v for k, v in _env.items() if v is not None})

RECIPES_DIR = Path(__file__).parent.parent / "data" / "recipes"
PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


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


def generate_weekly_plan(user_input: str) -> dict:
    """Ta fritext-input och returnera ett veckomenysförslag som dict."""
    recipes = _load_recipes()
    prompt_template = (PROMPTS_DIR / "weekly_planner.txt").read_text(encoding="utf-8")
    prompt = prompt_template.format(
        user_input=user_input,
        recipes=_recipe_summary(recipes),
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
