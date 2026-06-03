# Måltidsplaneraren — Användarmanual

> **Version:** 1.0 · **Plattform:** Synology NAS via Docker · **Gränssnitt:** Webbläsare

---

## Innehållsförteckning

1. [Översikt](#1-översikt)
2. [Öppna appen](#2-öppna-appen)
3. [Planera veckan](#3-planera-veckan)
4. [Handlingslistan](#4-handlingslistan)
5. [Recept](#5-recept)
6. [Varuhantering](#6-varuhantering)
7. [Säkerhetskopiera din data](#7-säkerhetskopiera-din-data)
8. [Spara NAS-anpassningar till git](#8-spara-nas-anpassningar-till-git)
9. [Uppdatera appen](#9-uppdatera-appen)
10. [Felsökning](#10-felsökning)

---

## 1. Översikt

Måltidsplaneraren är ett hushållsverktyg för veckoplanering av mat. Systemet löser tre saker:

| Funktion | Beskrivning |
|---|---|
| **Veckomeny** | AI föreslår middagar baserat på din fritext |
| **Handlingslista** | Rätt varor bockas automatiskt i när menyn godkänns |
| **Recept** | Läsbara recept direkt i mobilwebbläsaren |

**Typiskt veckoflöde:**

```
Skriv fritext → AI föreslår meny → Godkänn → Handlingslista klar → Handla
```

**Vem gör vad:**
- **Planering** sker på dator (PC/Mac)
- **Handlingslista och recept** används på mobil/platta i butiken

---

## 2. Öppna appen

Appen nås via webbläsaren på ditt lokala nätverk:

```
http://192.168.50.210:8501
```

Inga inloggningsuppgifter krävs. Appen är tillgänglig så länge NAS:en är igång.

> **Via VPN:** Om du är ansluten via OpenVPN når du appen på samma adress utifrån hemnätverket.

---

## 3. Planera veckan

### 3.1 Skriv vad du vill ha

Gå till fliken **Planera**. Skriv en fritext i inmatningsfältet och beskriv vad du är sugen på, vad du har hemma, eller hur veckan ser ut. Exempel:

- *"Något asiatiskt och något med kyckling, vi har ris hemma"*
- *"Lite enklare den här veckan, max 30 min per middag"*
- *"Vi har köttfärs som måste gå åt"*

Du kan även ange hur många portioner som ska planeras för (standard: 4).

### 3.2 Generera förslag

Klicka **Generera meny**. AI:n (Claude) tar fram ett veckomenysförslag med 5–7 middagar. Förslaget visas med recept, ingredienser och tillagningstid.

> Generering tar vanligtvis 10–20 sekunder.

### 3.3 Godkänn eller generera om

Läs igenom förslaget. Du har två val:

- **Godkänn menyn** — Handlingslistan fylls automatiskt i med alla ingredienser du behöver köpa. Mängder beräknas utifrån antal portioner.
- **Generera nytt förslag** — Ny begäran skickas till AI:n med samma fritext.

### 3.4 Omatchade ingredienser

Om ett recept innehåller en ingrediens som inte finns i varudatabasen (items.yaml) läggs den automatiskt till under **Extra denna vecka** i handlingslistan. Du ser ett meddelande om vilka som lades till.

> **Tips:** Lägg till ingrediensen permanent i Varuhantering så matchas den automatiskt nästa gång.

---

## 4. Handlingslistan

### 4.1 Navigera till listan

Klicka på **Handlingslista** i navigeringen. Listan är uppdelad efter butiksavdelningar (Frukt och grönt, Kött och chark, etc.) i den ordning du rör dig genom butiken.

### 4.2 Bocka av varor

Klicka i rutan bredvid en vara för att bocka av den. Ibockade varor visas med genomstruken text. Statusen sparas automatiskt — du kan stänga webbläsaren och öppna igen utan att förlora vad du bockat av.

> **Delad lista:** Två personer kan använda listan samtidigt på var sin enhet. Förändringar syns när man interagerar med appen nästa gång (t.ex. bockar av något).

### 4.3 Mängder

När en meny godkänts visas beräknade mängder bredvid varorna (t.ex. *600 g*, *3 dl*). Mängder för urcheckade varor visas med ~~genomstruken~~ grå text.

**Rensa mängder:** Knappen *Rensa mängder på urcheckade* tar bort mängdinformationen för varor du inte bockat i — utan att påverka ibockade varors mängder.

### 4.4 Extra varor

Under **Extra denna vecka** lägger du till engångsköp som inte finns i standardlistan (t.ex. *presenter*, *rengöringsmedel*). Skriv i textfältet och tryck Enter.

### 4.5 Butiksprofile

Om du handlar i olika butiker med olika avdelningsordning kan du välja profil i rullgardinsmenyn längst upp. Profiler skapar du och redigerar via **Redigera layout** (visas bara på dator).

### 4.6 Rensa listan

Knappen **Rensa bockat** tar bort bockningen på alla varor och nollställer listan inför nästa vecka.

---

## 5. Recept

### 5.1 Bläddra bland recept

Gå till fliken **Recept**. Alla recept visas som kort med titel, tillagningstid och svårighet. Klicka på ett recept för att se det i sin helhet — ingredienser, steg-för-steg-instruktioner och taggar.

Recepten är mobilanpassade och läsbara direkt i telefonens webbläsare.

### 5.2 Importera recept via URL

På dator syns knappen **Importera recept**. Klistra in webbadressen till ett recept (t.ex. från ICA, Arla, Tasteline) och klicka **Hämta**. Appen:

1. Hämtar sidan
2. Extraherar receptdata via AI
3. Visar en förhandsgranskning med ingredienser och instruktioner
4. Låter dig koppla ingredienser till varudatabasen
5. Sparar receptet efter din bekräftelse

> **Kostnad:** Receptimport använder Claude Haiku-modellen, ca 0,001–0,003 USD per recept.

### 5.3 Koppla ingredienser

Under importen kan du manuellt välja vilken vara i databasen som varje ingrediens motsvarar — eller godkänna den automatiska matchningen. Ingredienser utan koppling läggs till som fritext under Extra när recepet används.

### 5.4 Redigera recept

På dator visas knappen **Redigera** på varje recept. Du kan ändra:
- Titel, portioner, tillagningstid, svårighet, taggar
- Ingredienser (byta vara, ändra mängd och enhet)
- Tillagningssteg

Klicka **Spara** för att bekräfta. Ändringar sparas direkt i receptfilen på NAS:en.

### 5.5 Ta bort recept

Knappen **Ta bort** på ett recept ber om bekräftelse innan receptet raderas. Åtgärden kan inte ångras.

---

## 6. Varuhantering

Varuhantering nås via knappen **Hantera varor** på handlingsliste-sidan (visas bara på dator). Här hanterar du varudatabasen — de varor som kan matchas mot receptingredienser och visas i handlingslistan.

### 6.1 Lägga till en vara

Fyll i formuläret längst upp:

| Fält | Beskrivning |
|---|---|
| **Namn** | Varans svenska namn, t.ex. *havregryn* |
| **Kategori** | Butiksavdelning, t.ex. *Torrvaror* |
| **Enhet** | Standardmåttenhet, t.ex. *g*, *st*, *dl* |
| **Roll** | Se nedan |
| **Synonymer** | Alternativa namn, kommaseparerade, t.ex. *havreflingor, gröt* |

**Roller:**

| Roll | Beskrivning |
|---|---|
| Receptingrediens | Bockas in automatiskt från recept |
| Alltid hemma | Ingår i recept men behöver sällan köpas |
| Köps regelbundet | Mjölk, ägg, bröd — oavsett veckomeny |
| Hushållsartikel | Ej mat, hanteras manuellt |

ID genereras automatiskt från namnet och visas som förhandsgranskning.

### 6.2 Redigera en vara

Klicka på **✎** bredvid en vara i listan. Formuläret fylls i med varans nuvarande värden. Ändra det du vill och klicka **Spara ändringar**. Klicka **Avbryt** för att lämna utan att spara — formuläret töms.

> **OBS:** Varans ID kan inte ändras efter att den skapats — det används som referens i alla recept.

### 6.3 Ta bort en vara

Klicka på **✕** bredvid en vara. Om varan används i ett eller flera recept visas en varning med receptnamnen — borttagning blockeras tills du tagit bort varan ur recepten. Annars visas en bekräftelsedialog.

### 6.4 Söka och filtrera

Använd sökfältet och filtren för kategori och roll för att hitta specifika varor. Listan visar 50 varor per sida och pagineras vid behov.

---

## 7. Säkerhetskopiera din data

Innan varje uppdatering bör du säkerhetskopiera dina datafiler. Här är en sammanfattning av vad som lagras var:

| Fil | Innehåll | Hanteras av git? |
|---|---|---|
| `data/items.yaml` | Varudatabasen | **Ja** — kan påverkas av uppdatering |
| `data/recipes/*.yaml` | Alla recept | **Ja** — dina importerade recept är nya filer, ogiltigförklarade av git |
| `data/shopping_order.yaml` | Profiler och egna kategorier | Nej — ignoreras av git, aldrig i fara |
| `data/shopping_state.yaml` | Bockningsstatus | Nej — ignoreras av git, aldrig i fara |
| `data/weekly_plan.yaml` | Aktuell veckomeny | Nej — ignoreras av git |
| `data/settings.yaml` | Inställningar (hushållsstorlek m.m.) | Nej — ignoreras av git |

### 7.1 Manuell säkerhetskopiering

SSH:a in på NAS:en och kör:

```bash
cd /volume1/docker/maltidsplanerare

# Skapa en tidsstämplad backup
DATUM=$(date +%Y%m%d)
mkdir -p backups/$DATUM
cp data/items.yaml backups/$DATUM/
cp -r data/recipes/ backups/$DATUM/
echo "Backup skapad: backups/$DATUM"
```

### 7.2 Verifiera backup

```bash
ls -lh backups/$DATUM/
ls backups/$DATUM/recipes/ | wc -l   # Antal recept
```

---

## 8. Spara NAS-anpassningar till git

NAS:en är produktionsmiljön där alla verkliga ändringar sker — varor läggs till via Varuhantering, recept importeras via appen, befintliga recept redigeras. Dessa ändringar sparas i filer på disk men hamnar inte automatiskt i git. Utan ett aktivt steg kan en `git pull` skriva över dem.

Det här avsnittet förklarar vilka filer som berörs, hur du sparar dem, och vad som är best practice.

### 8.1 Vad som behöver sparas — och vad som är automatiskt säkert

| Fil / mapp | Spårad av git? | Risk vid `git pull` | Åtgärd |
|---|---|---|---|
| `data/items.yaml` | Ja | Kan skrivas över eller ge konflikt | Committa innan `git pull` |
| `data/recipes/*.yaml` (nya) | Nej — ej kända av git | Ingen — `git pull` tar aldrig bort otrackade filer | Rekommenderas ändå att committa |
| `data/recipes/*.yaml` (redigerade) | Ja, om originalet fanns i repot | Kan skrivas över om repot också ändrat filen | Committa innan `git pull` |
| `data/shopping_order.yaml` | Nej — i `.gitignore` | Ingen — profiler och kategorier bevaras alltid | Ingenting krävs |
| `data/settings.yaml` | Nej — i `.gitignore` | Ingen — git rör aldrig denna fil | Ingenting krävs |
| `data/shopping_state.yaml` | Nej — i `.gitignore` | Ingen | Ingenting krävs |
| `data/weekly_plan.yaml` | Nej — i `.gitignore` | Ingen | Ingenting krävs |

**Slutsats:** Det enda du aktivt behöver hantera är `data/items.yaml` och `data/recipes/`.

---

### 8.2 De tre alternativen

#### Alternativ A — Committa inför varje uppdatering (rekommenderat för de flesta)

Du committar NAS-data precis innan du hämtar ny kod. Enkelt, kräver inget extra upplägg.

```bash
cd /volume1/docker/maltidsplanerare
git add data/items.yaml data/recipes/
git commit -m "NAS: varor och recept $(date +%Y-%m-%d)"
git pull origin main
```

**Fördelar:** Enkelt. Inga extra verktyg.  
**Nackdelar:** Glömmer du steget före `git pull` riskerar du en konflikt.

---

#### Alternativ B — Committa direkt när du gjort ändringar

Du committar varje gång du avslutat en session i appen — lagt till varor, importerat recept eller redigerat ett recept.

```bash
cd /volume1/docker/maltidsplanerare
git add data/items.yaml data/recipes/
git commit -m "Lade till: havregryn, kokosmjölk"
git push origin main
```

**Fördelar:** Git-historiken reflekterar vad som faktiskt ändrades och när. Enkelt att se tillbaka.  
**Nackdelar:** Kräver disciplin — SSH-inloggning varje gång.

---

#### Alternativ C — Automatisera med ett script

Skapa ett script som committar och pushar all data-förändring. Kör det manuellt när du vill, eller schemalägg det via Synologys Task Scheduler.

```bash
# Skapa scriptet
cat > /volume1/docker/maltidsplanerare/scripts/spara_data.sh << 'EOF'
#!/bin/bash
set -e
cd /volume1/docker/maltidsplanerare
git config --global --add safe.directory /volume1/docker/maltidsplanerare

# Committa bara om något faktiskt ändrats
if ! git diff --quiet data/items.yaml data/recipes/; then
    git add data/items.yaml data/recipes/
    git commit -m "Auto: NAS-data $(date '+%Y-%m-%d %H:%M')"
    git push origin main
    echo "Data sparad till git."
else
    echo "Inga ändringar att spara."
fi
EOF
chmod +x /volume1/docker/maltidsplanerare/scripts/spara_data.sh
```

Kör scriptet:

```bash
bash /volume1/docker/maltidsplanerare/scripts/spara_data.sh
```

**Schemalägg i Synology Task Scheduler:** Kontrollpanelen → Uppgiftsschemaläggaren → Skapa → Schemalagd uppgift → Kör scriptet t.ex. varje natt kl 03:00.

**Fördelar:** Helt automatiskt. Inget att glömma.  
**Nackdelar:** Push till GitHub kräver att NAS:en har nätverksåtkomst och att git-autentisering är konfigurerad (SSH-nyckel eller token).

---

### 8.3 Konflikter i items.yaml — hur de uppstår och löses

En konflikt uppstår om **både** repot (via en PC-commit eller koduppdatering) och NAS:en har ändrat `items.yaml` sedan senaste sync. Git rapporterar det så här:

```
CONFLICT (content): Merge conflict in data/items.yaml
Automatic merge failed; fix conflicts and then commit the result.
```

Filen innehåller då markeringar:

```yaml
<<<<<<< HEAD
- id: silverlok
  name_sv: silverlök
=======
- id: schalottenlok
  name_sv: schalottenlök
>>>>>>> origin/main
```

**Lös det genom att välja en strategi:**

```bash
# Strategi 1: Behåll NAS-versionen (dina lokala varor, ignorera repots ändring)
git checkout --ours data/items.yaml
git add data/items.yaml
git commit -m "Bevarade NAS-version av items.yaml"

# Strategi 2: Ta in repots version (skriv över med repoversionen)
git checkout --theirs data/items.yaml
git add data/items.yaml
git commit -m "Tog in repots items.yaml"

# Strategi 3: Redigera filen manuellt och slå ihop det bästa från båda
nano data/items.yaml   # ta bort konfliktmarkeringarna, behåll båda varorna
git add data/items.yaml
git commit -m "Manuellt löst konflikt i items.yaml"
```

> **Bästa valet i de flesta situationer är Strategi 1** — dina lokala varor är det primära. Eventuellt nya varor från repot kan du lägga till via Varuhantering-gränssnittet efteråt.

---

### 8.4 Best practice — sammanfattning

1. **Committa alltid NAS-data innan `git pull`** — gör det till en rutin, inte ett undantag.
2. **Committa direkt efter session** om du jobbat mycket i Varuhantering eller importerat flera recept.
3. **Använd backup som säkerhetsnät** (avsnitt 7) — om något ändå går fel finns filerna lokalt.
4. **Välj Alternativ C (automatiserat script)** om du vill slippa tänka på det.
5. **Vid konflikt — välj `--ours`** om du inte vet vilket alternativ som är rätt. Det bevarar alltid NAS-data.

---

## 9. Uppdatera appen — steg för steg

Uppdateringar görs i tre steg: (1) merga på GitHub, (2) hämta kod till NAS, (3) bygga om Docker.

### Steg 1 — Merga pull request på GitHub

1. Gå till `https://github.com/GMW83/Maltidsplanerare/pulls`
2. Öppna den aktuella pull requesten
3. Klicka **Merge pull request** → **Confirm merge**

### Steg 2 — Hämta ny kod till NAS

SSH:a in på NAS:en:

```bash
ssh admin@192.168.50.210
cd /volume1/docker/maltidsplanerare
```

**Säkerhetskopiera alltid först** (se avsnitt 7.1), sedan:

```bash
git pull origin main
```

#### Om git rapporterar konflikt i items.yaml

Det händer om du lagt till varor lokalt via Varuhantering OCH en uppdatering ändrade items.yaml i repot. Git stoppar och visar något liknande:

```
CONFLICT (content): Merge conflict in data/items.yaml
```

Lös det så här:

```bash
# Se vad som skiljer sig
git diff data/items.yaml

# Alternativ A — behåll din lokala version (dina egna varor)
git checkout --ours data/items.yaml
git add data/items.yaml
git commit -m "Bevarade lokala varor vid merge"

# Alternativ B — ta in upstream-version (repoversionen)
git checkout --theirs data/items.yaml
git add data/items.yaml
git commit -m "Tog in uppdaterad items.yaml"
```

> **Tips:** Alternativ A är det säkra valet om du vet att du lagt till varor sedan förra uppdateringen. Du kan sedan manuellt lägga till eventuella nya varor från repot via Varuhantering-gränssnittet.

#### Om det är första gången du kör git pull (ny installation)

Om katalogen inte är ett git-repo sedan tidigare:

```bash
# Kör en gång för att sätta upp
git config --global --add safe.directory /volume1/docker/maltidsplanerare
git init
git remote add origin https://github.com/GMW83/Maltidsplanerare.git
git fetch origin main

# Säkerhetskopiera INNAN du kör detta
git reset --hard origin/main
```

### Steg 3 — Bygg om Docker och starta om

```bash
sudo docker compose build && sudo docker compose up -d
```

Bygget tar 1–3 minuter. När det är klart ser du:

```
✔ Container maltidsplanerare  Started
```

Öppna `http://192.168.50.210:8501` och verifiera att appen fungerar.

### Steg 4 — Verifiera att data är intakt

Kontrollera snabbt i appen:
- [ ] Varudatabasen innehåller dina varor (Hantera varor)
- [ ] Dina recept visas under Recept
- [ ] Handlingslistan ser korrekt ut

---

## 10. Felsökning

### Appen svarar inte / kan inte nås

**Kontrollera att containern körs:**

```bash
sudo docker ps | grep maltidsplanerare
```

Om den inte visas, starta den:

```bash
cd /volume1/docker/maltidsplanerare
sudo docker compose up -d
```

**Kontrollera loggar:**

```bash
sudo docker compose logs --tail=50
```

---

### `permission denied` vid Docker-kommandon

Kör med `sudo`:

```bash
sudo docker compose build && sudo docker compose up -d
```

---

### `fatal: detected dubious ownership` vid git

```bash
git config --global --add safe.directory /volume1/docker/maltidsplanerare
```

Kör sedan git-kommandot igen. Felet uppstår när katalogen ägs av en annan användare (t.ex. root) än den som kör git (t.ex. admin).

---

### AI-genereringen misslyckas / inga förslag visas

1. Kontrollera att `.env`-filen finns och innehåller en giltig API-nyckel:

```bash
cat /volume1/docker/maltidsplanerare/.env
# Ska visa: ANTHROPIC_API_KEY=sk-ant-...
```

2. Kontrollera att API-nyckeln inte har löpt ut på [console.anthropic.com](https://console.anthropic.com)

3. Kontrollera loggar för felmeddelande:

```bash
sudo docker compose logs --tail=100 | grep -i error
```

---

### Receptimport misslyckas

- **Sidan kräver JavaScript:** Många receptsajter renderas via JavaScript vilket gör att appen inte kan hämta receptet. Prova en annan sajt eller kopiera ingredienser manuellt.
- **Timeout:** Sidan svarade inte inom 15 sekunder. Prova igen.
- **AI returnerade ogiltigt format:** Kontrollera loggar. Prova att importera igen — det är ovanligt men kan hända.

---

### Varor jag lagt till via Varuhantering försvann efter uppdatering

`data/items.yaml` är versionshanterad. Om en `git reset --hard` kördes utan att spara backup skrevs filen över.

**Återställ från backup:**

```bash
cp /volume1/docker/maltidsplanerare/backups/YYYYMMDD/items.yaml \
   /volume1/docker/maltidsplanerare/data/items.yaml
```

Ersätt `YYYYMMDD` med datumet för din senaste backup. Starta om containern:

```bash
sudo docker compose restart
```

---

### Recept saknas efter uppdatering

Recept som du importerat är nya filer som inte finns i git-repot — de påverkas normalt **inte** av `git pull`. De kan dock försvinna vid `git reset --hard` om det kördes utan backup.

**Återställ från backup:**

```bash
cp /volume1/docker/maltidsplanerare/backups/YYYYMMDD/recipes/*.yaml \
   /volume1/docker/maltidsplanerare/data/recipes/
sudo docker compose restart
```

---

### Varningsmeddelande: `buildx: failed to read current commit information`

```
WARN[0000] buildx: failed to read current commit information with git rev-parse --is-inside-work-tree
```

Ofarligt. Docker Buildx försöker hämta git-metadata men katalogägaren matchar inte. Påverkar inte appen.

---

### Handlingslistan visar fel status / gammal data

Tryck på valfritt element i appen (t.ex. bocka av en vara) för att trigga en refresh. Appen läser alltid färsk data från fil vid varje interaktion.

---

## Bilaga — Snabbreferens för uppdatering

```bash
# 1. SSH in
ssh admin@192.168.50.210
cd /volume1/docker/maltidsplanerare

# 2. Spara NAS-anpassningar till git (ALLTID innan git pull)
git add data/items.yaml data/recipes/
git commit -m "NAS: varor och recept $(date +%Y-%m-%d)"
git push origin main

# 3. Backup (extra säkerhetsnät)
DATUM=$(date +%Y%m%d)
mkdir -p backups/$DATUM
cp data/items.yaml backups/$DATUM/
cp -r data/recipes/ backups/$DATUM/

# 4. Hämta ny kod (efter merge på GitHub)
git pull origin main
# Vid konflikt i items.yaml: git checkout --ours data/items.yaml && git add data/items.yaml && git commit -m "Bevarade NAS-data"

# 5. Bygg om och starta
sudo docker compose build && sudo docker compose up -d

# 6. Verifiera
sudo docker ps | grep maltidsplanerare
```

---

*Senast uppdaterad: maj 2026*

---

## Design-prompt (för Claude / Figma / designverktyg)

Klistra in följande prompt i ditt designverktyg för att få ett snyggt layoutförslag för denna manual:

---

> **Prompt:**
>
> Skapa en layout för en teknisk användarmanual med följande egenskaper:
>
> - **Stil:** Ren, modern och lättläst. Inspirerad av Apple-dokumentation eller Notion-guider. Varm, jordnära färgpalett med olivgrönt som accentfärg (#6B7C3E eller liknande), cremevit bakgrund och mörkgrå text.
> - **Struktur:** Fast sidebar till vänster med klickbar innehållsförteckning. Huvudinnehåll i mitten med max 720px bredd. Rikligt med luft och tydliga sektionsgränser.
> - **Typografi:** Rubriker i en sans-serif (t.ex. Inter eller DM Sans), brödtext i läsbar storlek (16–17px), radavstånd 1.6.
> - **Kodblock:** Mörk bakgrund (#1E1E1E), monospace-font, subtil rundning. Syntax-highlighting för bash-kommandon.
> - **Infoboxar:** Tre varianter — blå info-ruta, gul varning, röd fara. Avrundade hörn, liten ikon till vänster.
> - **Tabeller:** Randig bakgrund varannan rad, tunn border, header i olivgrön.
> - **Mobilvy:** Sidebar kollapsar till hamburger-meny. Kodblock scrollar horisontellt.
> - **Övrigt:** Aktiv sektion i sidebar highlightas. Smooth scroll vid klick på innehållsförteckning. Fästbar header med manualtitel och nuvarande sektionsnamn.
>
> Innehållet är på svenska och handlar om en hushållsapp för måltidsplanering som körs på en Synology NAS via Docker.
