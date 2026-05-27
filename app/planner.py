"""AI-planering via Claude API — fritext-input → veckomenysförslag."""

import json
import os
from pathlib import Path

import anthropic
import yaml
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

RECIPES_DIR = Path(__file__).parent.parent / "data" / "recipes"
PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


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
            f"(tags: {tags}, "
            f"tid: {meta.get('cook_time_minutes', '?')} min)"
        )
    return "\n".join(lines)


def generate_weekly_plan(user_input: str) -> dict:
    """Skicka fritext-input till Claude och returnera veckomenysförslag som dict."""
    recipes = _load_recipes()

    prompt_template = (PROMPTS_DIR / "weekly_planner.txt").read_text(encoding="utf-8")
    prompt = prompt_template.format(
        user_input=user_input,
        recipes=_recipe_summary(recipes),
    )

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1].rsplit("```", 1)[0]

    return json.loads(raw)
