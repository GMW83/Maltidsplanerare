"""URL-import av recept via Claude API."""

import json
import os
import re
import unicodedata
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from dotenv import dotenv_values

_env_path = Path(__file__).parent.parent / ".env"
_env = dotenv_values(_env_path)
os.environ.update({k: v for k, v in _env.items() if v is not None})

import anthropic

RECIPES_DIR = Path(__file__).parent.parent / "data" / "recipes"

# Haiku används för extrahering — mekanisk struktureringsuppgift, behöver ej Sonnet
_MODEL = "claude-haiku-4-5-20251001"

_SYSTEM = """Du är ett recept-extraheringsverktyg. Extrahera receptet från given data och returnera ENBART JSON (inga kodblock, ingen förklarande text):

{
  "title": "Receptnamn",
  "servings": 4,
  "ingredients": [
    {"name": "kycklingfilé", "amount": 500, "unit": "g"},
    {"name": "gul lök", "amount": 1, "unit": "st"}
  ],
  "instructions": [
    {"step": 1, "text": "Hacka löken fint."},
    {"step": 2, "text": "Stek löken mjuk i olja på medelvärme."}
  ],
  "tags": ["vardag", "kyckling"],
  "cook_time_minutes": 30,
  "difficulty": 2
}

Regler:
- amount är alltid ett tal (heltal eller decimal, aldrig sträng)
- difficulty: 1 = lätt, 2 = medel, 3 = svår
- Ingrediensnamn och instruktioner på svenska — översätt om originalet är på annat språk
- tags: 2–5 korta beskrivande ord
- VIKTIGT: Skriv RENA ingrediensnamn utan parenteser, underrubriker eller kontexthänvisningar.
  FEL: "grädde (köttbullar)", "smör (att steka i)", "salt (sås)"
  RÄTT: "grädde", "smör", "salt"
- Om samma ingrediens förekommer i flera delar av receptet: slå ihop till EN rad med total mängd.
  FEL: grädde 1 dl + grädde 0.75 dl + grädde 3 dl  (tre rader)
  RÄTT: grädde 4.75 dl  (en rad, summan)"""


def _client():
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raise ValueError("ANTHROPIC_API_KEY saknas i .env")
    return anthropic.Anthropic(api_key=key)


def fetch_url(url: str) -> str:
    headers = {"User-Agent": "Mozilla/5.0 (compatible; RecipeImporter/1.0)"}
    r = requests.get(url, headers=headers, timeout=15)
    r.raise_for_status()
    return r.text


def _extract_jsonld(html: str) -> dict | None:
    """Försök hitta schema.org/Recipe som JSON-LD — ger minimalt tokenanvändning."""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(tag.string or "")
            # Kan vara lista eller dict
            if isinstance(data, list):
                data = next((d for d in data if isinstance(d, dict) and d.get("@type") == "Recipe"), None)
            if isinstance(data, dict):
                if data.get("@type") == "Recipe":
                    return data
                # @graph-struktur
                for item in data.get("@graph", []):
                    if isinstance(item, dict) and item.get("@type") == "Recipe":
                        return item
        except (json.JSONDecodeError, AttributeError, TypeError):
            continue
    return None


def _strip_html(html: str) -> str:
    """Ta bort skräpelement och returnera ren recepttext — ~90% färre tokens än rå HTML."""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header",
                     "aside", "iframe", "noscript", "meta", "link"]):
        tag.decompose()
    text = soup.get_text(separator="\n", strip=True)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text[:12000]


def extract_recipe(html: str, url: str) -> dict:
    """Extrahera receptdata från HTML via Claude API (Haiku-modellen)."""
    jsonld = _extract_jsonld(html)
    if jsonld:
        # Strukturerad data finns — minimalt anrop
        content = (
            f"URL: {url}\n\n"
            f"Strukturerad receptdata (schema.org/Recipe):\n"
            f"{json.dumps(jsonld, ensure_ascii=False)[:8000]}"
        )
    else:
        # Fallback: rensad text i stället för rå HTML
        content = f"URL: {url}\n\nReceptsida (rensad text):\n{_strip_html(html)}"

    msg = _client().messages.create(
        model=_MODEL,
        max_tokens=2048,
        system=_SYSTEM,
        messages=[{"role": "user", "content": content}],
    )
    raw = msg.content[0].text.strip()
    raw = re.sub(r"^```(?:json)?\s*\n?", "", raw)
    raw = re.sub(r"\n?```\s*$", "", raw)
    return json.loads(raw)


def match_ingredients(ingredients: list[dict], items_db: dict) -> list[dict]:
    """
    Matcha extraherade ingredienser mot items_db {id: item}.
    Returnerar listan utökt med 'matched_id' (str|None) per post.
    Använder enbart exakt matchning — ingen delsträngsmatchning — för att
    undvika felaktiga kopplingar som salt→sardeller eller smör→hjärtsallad.
    """
    results = []
    for ing in ingredients:
        name_lower = ing["name"].lower().strip()
        matched_id = None

        for item_id, item in items_db.items():
            if item["name_sv"].lower() == name_lower:
                matched_id = item_id
                break
            for syn in item.get("synonyms", []):
                if syn.lower() == name_lower:
                    matched_id = item_id
                    break
            if matched_id:
                break

        results.append({**ing, "matched_id": matched_id})
    return results


def build_recipe_id(title: str) -> str:
    """Generera unikt recipe_id från titel."""
    nfd = unicodedata.normalize("NFD", title.lower())
    ascii_t = "".join(c for c in nfd if unicodedata.category(c) != "Mn")
    slug = re.sub(r"[^a-z0-9]+", "_", ascii_t).strip("_")
    for i in range(1, 100):
        rid = f"{slug}_{i:03d}"
        if not (RECIPES_DIR / f"{rid}.yaml").exists():
            return rid
    return f"{slug}_xxx"


def _name_to_id(name: str) -> str:
    nfd = unicodedata.normalize("NFD", name.lower())
    ascii_n = "".join(c for c in nfd if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", "_", ascii_n).strip("_")


def _safe_amount(v):
    try:
        f = float(v)
        return int(f) if f == int(f) else round(f, 2)
    except (ValueError, TypeError):
        return v


def build_recipe_dict(raw: dict, matches: list[dict], overrides: dict, url: str) -> dict:
    """
    Bygg en komplett receptdict redo att sparas.
    overrides: {idx: item_id} för ingredienser där användaren valt annan koppling.
    """
    ingredients = []
    for i, m in enumerate(matches):
        ingredient_id = overrides.get(i) or m["matched_id"] or _name_to_id(m["name"])
        ingredients.append({
            "ingredient_id": ingredient_id,
            "amount": _safe_amount(m["amount"]),
            "unit": m["unit"],
        })

    return {
        "recipe_id": build_recipe_id(raw["title"]),
        "title": raw["title"],
        "servings": raw.get("servings", 4),
        "ingredients": ingredients,
        "instructions": raw.get("instructions", []),
        "tags": raw.get("tags", []),
        "metadata": {
            "cook_time_minutes": raw.get("cook_time_minutes", 30),
            "difficulty": raw.get("difficulty", 2),
            "source_url": url,
        },
    }
