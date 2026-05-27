"""CLI-verktyg för att planera veckans måltider."""

import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent.parent))
from app.planner import generate_weekly_plan

PLAN_PATH = Path(__file__).parent.parent / "data" / "weekly_plan.yaml"


def main():
    print("=" * 40)
    print("  Måltidsplanerare")
    print("=" * 40)
    print("\nVad vill ni äta den här veckan?")
    print("(t.ex. 'något asiatiskt och något med kyckling')\n")
    user_input = input("> ").strip()

    if not user_input:
        print("Ingen input angiven. Avslutar.")
        sys.exit(0)

    print("\nGenererar förslag, vänligen vänta...")

    try:
        plan = generate_weekly_plan(user_input)
    except Exception as e:
        print(f"\nFel vid anrop till Claude API: {e}")
        sys.exit(1)

    print("\n" + "=" * 40)
    print("  Förslag på veckomeny")
    print("=" * 40)
    for meal in plan["meals"]:
        print(f"  {meal['day'].capitalize():<12} {meal['title']}")

    print("\nGodkänner du förslaget? (j = ja, n = generera nytt)")
    answer = input("> ").strip().lower()

    if answer == "j":
        with open(PLAN_PATH, "w", encoding="utf-8") as f:
            yaml.dump(plan, f, allow_unicode=True, sort_keys=False)
        print(f"\nVeckoplan sparad i {PLAN_PATH.relative_to(Path.cwd()) if PLAN_PATH.is_relative_to(Path.cwd()) else PLAN_PATH}")
    else:
        print("\nIngen plan sparad. Kör skriptet igen för ett nytt förslag.")


if __name__ == "__main__":
    main()
