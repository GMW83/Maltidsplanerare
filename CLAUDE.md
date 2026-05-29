# Maltidsplanerare — Projektkontext

## Vad projektet är

Ett hushållsverktyg för veckoplanering av mat. Inte en receptapp — ett planeringsverktyg med tre outputs:

1. **Veckomeny** — AI föreslår baserat på fritext-input
2. **Handlingslista** — strukturerad efter Coops butiksavdelningar, rätt varor auto-ibockade
3. **Recept** — läsbara i mobilwebbläsare

## Användarsituation

- Hushåll (familj), inte enbart en person
- Planering sker på dator
- Handlingslista och recept används på mobil/platta via webbläsare (http)
- Idag används OneNote för handlingslistan — ersätts av det här systemet

## Hur det används

Användaren skriver fritext som input, t.ex.:
- "något asiatiskt och något med kyckling"
- "vi har bönar hemma, gör något med det"
- "lite enklare den här veckan"

AI (Claude API) genererar ett veckomenysförslag. Användaren godkänner. Handlingslistan bockas automatiskt i med de ingredienser som behövs.

## Viktiga avgränsningar (v1)

- **Inget** automatiskt inventariehantering — inventariet anges som fritext vid planering
- **Inga** erbjudanden i v1 — kan läggas till senare via PDF-upload eller mail
- **Ingen** historik — handlingslistan är bara för aktuell vecka
- AI föreslår alltid, användaren godkänner alltid innan något sparas

## Teknisk stack

| Del | Val |
|---|---|
| UI | Streamlit (webb, mobilanpassad) |
| Backend | Python |
| Data | YAML |
| AI | Claude API |
| Hosting | Lokalt till en början, Docker/Synology senare |

## Mappstruktur (planerad)

```
Maltidsplanerare/
├── data/
│   ├── items.yaml          # Varudatabas, strukturerad efter Coops avdelningar
│   ├── recipes/            # En YAML-fil per recept
│   └── weekly_plan.yaml    # Aktuell veckomeny (skrivs över varje vecka)
├── app/
│   ├── main.py             # Streamlit-app, entry point
│   ├── planner.py          # AI-planering, Claude API-anrop
│   ├── shopping.py         # Handlingslista-logik
│   ├── recipes.py          # Recepthantering
│   └── importer.py         # URL-import av recept
├── prompts/
│   └── weekly_planner.txt  # Prompt-mall för veckoplaneringen
├── scripts/
│   ├── validate_recipe.py  # Validera receptformat
│   └── import_url.py       # CLI-verktyg för URL-import
├── CLAUDE.md
├── README.md
└── requirements.txt
```

## Dataschema

### items.yaml — varudatabas

Strukturerad efter Coops butiksavdelningar. Varje vara har ett stabilt ID i snake_case.

```yaml
- id: yellow_onion
  name_sv: gul lök
  category: frukt_och_gront
  unit: g
  synonyms:
    - gullök
    - lök

- id: chicken_fillet
  name_sv: kycklingfilé
  category: kott_och_chark
  unit: g
  synonyms:
    - kyckling
```

Kategorier (butiksavdelningar i Coop):
- `frukt_och_gront`
- `kott_och_chark`
- `mejeri_och_agg`
- `torrvaror`
- `konserver`
- `frysta_varor`
- `brod_och_bakverk`
- `drycker`
- `kryddor_och_smaksattare`
- `ovrigt`

### Receptformat (YAML)

```yaml
recipe_id: chicken_tikka_001
title: Chicken Tikka Masala
servings: 4
ingredients:
  - ingredient_id: chicken_fillet
    amount: 700
    unit: g
  - ingredient_id: yellow_onion
    amount: 200
    unit: g
instructions:
  - step: 1
    text: Hacka lök och vitlök fint.
  - step: 2
    text: Stek löken mjuk i olja.
tags:
  - indiskt
  - starkt
  - vardag
metadata:
  cook_time_minutes: 40
  difficulty: 2
  spice_level: 4
```

## Byggplan — var vi är

### Fas 1 — Datafundament
- [x] Steg 1.1: Mappstruktur och grundfiler
- [x] Steg 1.2: `items.yaml` med vanliga råvaror per butiksavdelning
- [x] Steg 1.3: Receptschema + 5 exempelrecept manuellt inmatade

### Fas 2 — AI-planering ← NÄSTA FAS
- [x] Steg 2.1: Claude API-integration (Python-modul)
- [x] Steg 2.2: Fritext-input → veckomenysförslag
- [x] Steg 2.3: Godkännandeflöde (CLI till en början)

### Fas 3 — Streamlit-app
- [x] Steg 3.1: Grundapp med tre sidor (Planera / Handlingslista / Recept)
- [x] Steg 3.2: Handlingslista med auto-ibockning, mobilanpassad
- [x] Steg 3.3: Receptvisare, mobilanpassad
- [x] Steg 3.4: Olivgrönt tema, bottenmeny, single-page-arkitektur
- [x] Steg 3.5: Persistent handlingslista (shopping_state.yaml) — full lista, förbockad-modell

### Fas 4 — URL-import
- [ ] Steg 4.1: URL-parser via Claude API
- [ ] Steg 4.2: Godkännandeflöde för importerade recept

## Designprinciper

- AI föreslår alltid — applikationen validerar, sparar, skriver
- Stabila ID:n i snake_case på alla ingredienser
- Nya ingredienser kräver alltid användargodkännande innan de läggs till i items.yaml
- Modulär kod — en fil per ansvarsområde
- Enkelt och överblickbart framför smart och komplext
