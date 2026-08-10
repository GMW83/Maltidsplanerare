# Måltidsplaneraren — Användarmanual

> **Version:** 1.0 · **Plattform:** Synology NAS via Docker · **Gränssnitt:** Webbläsare

---

## Innehållsförteckning

1. [Översikt](#1-översikt)
2. [Öppna appen](#2-öppna-appen)
3. [Startsidan](#3-startsidan)
4. [Planera veckan](#4-planera-veckan)
5. [Handlingslistan](#5-handlingslistan)
6. [Recept](#6-recept)
7. [Varuhantering](#7-varuhantering)
8. [Säkerhetskopiera din data](#8-säkerhetskopiera-din-data)
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

## 3. Startsidan

Fliken **🏠 Hem** är det första du ser. Här visas den planerade menyn för en vald vecka.

### 3.1 Välj vecka

Överst finns en väljare med **Denna vecka** och **Nästa vecka**. Byt mellan dem för att se respektive veckas planerade middagar. Standard är denna vecka.

### 3.2 Visad meny

- Är veckan planerad visas alla middagar som kort (dag + rätt).
- Är veckan inte planerad visas *"Ingen meny planerad"* — gå då till fliken **Planera**.

Längst ner finns även en länk till denna användarmanual.

---

## 4. Planera veckan

### 4.1 Välj vecka att planera

Gå till fliken **📅 Planera**. Överst väljer du **Planera för: Denna vecka** eller **Nästa vecka**. Du kan planera båda veckorna — de sparas var för sig och skriver inte över varandra.

> Om en plan redan finns för den valda veckan visas en varning om att den skrivs över om du godkänner ett nytt förslag.

### 4.2 Välj dagar

Under **Välj dagar** bockar du i vilka veckodagar (mån–sön) som ska planeras. För innevarande vecka är redan passerade dagar avstängda så att du bara planerar framåt.

### 4.3 Skriv vad du vill ha

Skriv en fritext och beskriv vad du är sugen på, vad du har hemma, eller hur veckan ser ut. Exempel:

- *"Något asiatiskt och något med kyckling, vi har ris hemma"*
- *"Lite enklare den här veckan, max 30 min per middag"*
- *"Vi har köttfärs som måste gå åt"*

Du kan även ange hur många portioner som ska planeras för (standard: 4).

### 4.4 Generera förslag

Klicka **Generera förslag**. AI:n (Claude) tar fram ett menysförslag för de valda dagarna. Förslaget visas med en rätt per dag.

> Generering tar vanligtvis 10–20 sekunder.

### 4.5 Justera, godkänn eller generera om

Läs igenom förslaget. Du kan:

- **Byta ut en enskild rätt** — klicka på **↺** bredvid en dag så föreslår AI:n ett alternativ för just den dagen.
- **Generera ett helt nytt förslag** — klicka **Generera förslag** igen.
- **Godkänna** — klicka **✓ Godkänn och spara veckoplan**. Veckoplanen sparas och handlingslistan fylls automatiskt i med alla ingredienser du behöver köpa. Mängder beräknas utifrån antal portioner.

### 4.6 Omatchade ingredienser

Om ett recept innehåller en ingrediens som inte finns i varudatabasen (items.yaml) läggs den automatiskt till under **Extra denna vecka** i handlingslistan. Du ser ett meddelande om vilka som lades till.

> **Tips:** Lägg till ingrediensen permanent i Varuhantering så matchas den automatiskt nästa gång.

### 4.7 Flera veckor och automatiskt veckoskifte

Denna vecka och nästa vecka lagras separat och påverkar inte varandra. När en ny vecka börjar (på måndagen) blir **"nästa vecka" automatiskt "denna vecka"** — du behöver inte göra något manuellt. Sedan kan du planera en ny nästa vecka igen.

---

## 5. Handlingslistan

### 5.1 Navigera till listan

Klicka på **🛒 Lista** i navigeringen. Listan är uppdelad efter butiksavdelningar (Frukt och grönt, Kött och chark, etc.) i den ordning du rör dig genom butiken.

### 5.2 Bocka av varor

Klicka i rutan bredvid en vara för att bocka av den. Ibockade varor visas med genomstruken text. Statusen sparas automatiskt — du kan stänga webbläsaren och öppna igen utan att förlora vad du bockat av.

> **Delad lista:** Två personer kan använda listan samtidigt på var sin enhet. Förändringar syns när man interagerar med appen nästa gång (t.ex. bockar av något).

### 5.3 Mängder

När en meny godkänts visas beräknade mängder bredvid varorna (t.ex. *600 g*, *3 dl*). Mängder för urcheckade varor visas med ~~genomstruken~~ grå text.

**Flera veckor adderas:** Planerar du både denna och nästa vecka summeras mängderna i listan — finns samma ingrediens i båda veckornas recept visas den totala mängden.

**Rensa mängder:** Knappen *Rensa mängder på urcheckade* (visas när det finns urcheckade varor med mängd) tar bort mängdinformationen för varor du inte bockat i — utan att påverka ibockade varors mängder.

### 5.4 Extra varor

Under **Extra denna vecka** lägger du till engångsköp som inte finns i standardlistan (t.ex. *presenter*, *rengöringsmedel*). Skriv i textfältet och tryck på **＋**.

### 5.5 Butiksprofil

Om du handlar i olika butiker med olika avdelningsordning kan du välja profil i rullgardinsmenyn längst upp. Profiler skapar du och redigerar via **Redigera layout** (visas bara på dator).

---

## 6. Recept

### 6.1 Bläddra bland recept

Gå till fliken **📖 Recept**. Överst finns en filterrad: **Alla recept**, **Denna vecka** och **Nästa vecka**.

- **Alla recept** — visar samtliga recept och ett sökfält för att filtrera på titel.
- **Denna vecka** / **Nästa vecka** — visar bara recepten i den valda veckans planerade meny. Saknas en plan visas *"Ingen meny planerad för …"*.

Välj ett recept i listan för att se det i sin helhet — ingredienser, steg-för-steg-instruktioner och taggar. Recepten är mobilanpassade och läsbara direkt i telefonens webbläsare.

### 6.2 Importera recept via URL

På dator syns knappen **Importera recept**. Klistra in webbadressen till ett recept (t.ex. från ICA, Arla, Tasteline) och klicka **Hämta**. Appen:

1. Hämtar sidan
2. Extraherar receptdata via AI
3. Visar en förhandsgranskning med ingredienser och instruktioner
4. Låter dig koppla ingredienser till varudatabasen
5. Sparar receptet efter din bekräftelse

> **Kostnad:** Receptimport använder Claude Haiku-modellen, ca 0,001–0,003 USD per recept.

### 6.3 Koppla ingredienser

Under importen kan du manuellt välja vilken vara i databasen som varje ingrediens motsvarar — eller godkänna den automatiska matchningen. Ingredienser utan koppling läggs till som fritext under Extra när recepet används.

### 6.4 Redigera recept

På dator visas knappen **Redigera** på varje recept. Du kan ändra:
- Titel, portioner, tillagningstid, svårighet, taggar
- Ingredienser (byta vara, ändra mängd och enhet)
- Tillagningssteg

Klicka **Spara** för att bekräfta. Ändringar sparas direkt i receptfilen på NAS:en.

### 6.5 Ta bort recept

Knappen **Ta bort** på ett recept ber om bekräftelse innan receptet raderas. Åtgärden kan inte ångras.

---

## 7. Varuhantering

Varuhantering nås via knappen **Hantera varor** på handlingsliste-sidan (visas bara på dator). Här hanterar du varudatabasen — de varor som kan matchas mot receptingredienser och visas i handlingslistan.

### 7.1 Lägga till en vara

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

### 7.2 Redigera en vara

Klicka på **✎** bredvid en vara i listan. Formuläret fylls i med varans nuvarande värden. Ändra det du vill och klicka **Spara ändringar**. Klicka **Avbryt** för att lämna utan att spara — formuläret töms.

> **OBS:** Varans ID kan inte ändras efter att den skapats — det används som referens i alla recept.

### 7.3 Ta bort en vara

Klicka på **✕** bredvid en vara. Om varan används i ett eller flera recept visas en varning med receptnamnen — borttagning blockeras tills du tagit bort varan ur recepten. Annars visas en bekräftelsedialog.

### 7.4 Söka och filtrera

Använd sökfältet och filtren för kategori och roll för att hitta specifika varor. Listan visar 50 varor per sida och pagineras vid behov.

---

## 8. Säkerhetskopiera din data

All din data — varor, recept, profiler, handlingslista — lagras i `data/`-mappen på NAS:en och ignoreras helt av git. Det betyder att `git pull` aldrig kan skriva över eller ta bort din data.

| Fil | Innehåll | Påverkas av `git pull`? |
|---|---|---|
| `data/items.yaml` | Varudatabasen | Nej — ignoreras av git |
| `data/recipes/*.yaml` | Alla recept | Nej — ignoreras av git |
| `data/shopping_order.yaml` | Profiler och egna kategorier | Nej — ignoreras av git |
| `data/shopping_state.yaml` | Bockningsstatus | Nej — ignoreras av git |
| `data/weekly_plan.yaml` | Aktuell veckomeny | Nej — ignoreras av git |
| `data/settings.yaml` | Inställningar (hushållsstorlek m.m.) | Nej — ignoreras av git |

Backup rekommenderas ändå inför uppdateringar — som skydd mot mänskliga misstag.

### 8.1 Manuell säkerhetskopiering

SSH:a in på NAS:en och kör:

```bash
cd /volume1/docker/maltidsplanerare

# Skapa en tidsstämplad backup
DATUM=$(date +%Y%m%d)
mkdir -p backups/$DATUM
cp -r data/ backups/$DATUM/
echo "Backup skapad: backups/$DATUM"
```

### 8.2 Verifiera backup

```bash
ls -lh backups/$DATUM/
ls backups/$DATUM/recipes/ | wc -l   # Antal recept
```

### 8.3 Flytta data till ny maskin

Eftersom all data ligger i `data/`-mappen är det enkelt att flytta:

```bash
# Kopiera data från NAS till annan maskin (kör från mottagarmaskinen)
scp -r admin@192.168.50.210:/volume1/docker/maltidsplanerare/data/ ./data/
```

---

## 9. Uppdatera appen — steg för steg

Uppdateringar görs i tre steg: (1) merga på GitHub, (2) hämta kod till NAS, (3) bygga om Docker. Din data påverkas inte.

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

Säkerhetskopiera om du vill (se avsnitt 8.1), sedan:

```bash
git pull origin main
```

Din data i `data/`-mappen påverkas inte av pull:en. Git-kommandon körs som `admin` — inget `sudo` behövs.

> Får du `Your local changes would be overwritten by merge` beror det nästan alltid på DSM:s filrättigheter. Se avsnitt 10, och kör engångsfixen `git config core.fileMode false`.

#### Om det är första gången du kör git pull (ny installation)

Om katalogen inte är ett git-repo sedan tidigare:

```bash
# Kör en gång för att sätta upp
git config --global --add safe.directory /volume1/docker/maltidsplanerare
git init
git remote add origin https://github.com/GMW83/Maltidsplanerare.git
git fetch origin main
git config core.fileMode false   # DSM sätter exekveringsbit — annars strular varje pull

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

> **Bara Docker-kommandon behöver `sudo`.** Alla git-kommandon (`git pull`, `git config`, `git status` m.fl.) körs som vanlig `admin`-användare. Kör du git med `sudo` skapas filer som ägs av root, vilket orsakar nya rättighetsproblem — undvik det.

---

### `Your local changes would be overwritten by merge` vid `git pull`

Typiskt på Synology. Kontrollera först vad som faktiskt skiljer:

```bash
git diff --stat
git diff app/style.py | head -20
```

Ser du `0 insertions(+), 0 deletions(-)` på alla filer, och diffen bara visar rader som dessa:

```
old mode 100644
new mode 100755
```

…är det **inte** dina ändringar. DSM sätter exekveringsbiten (`755`) på filer i delade mappar, och git spårar den biten — därför ser git varenda fil som ändrad trots att innehållet är identiskt.

**Permanent lösning — kör en gång:**

```bash
cd /volume1/docker/maltidsplanerare
git config core.fileMode false
```

Git struntar därefter i exekveringsbiten i det här repot, och `git pull` fungerar normalt i fortsättningen. Inget innehåll går förlorat, eftersom skillnaden bara var rättigheter. Kommandot kräver inte `sudo`.

Visar diffen däremot **verkliga kodrader**, har någon ändrat filerna på NAS:en. Ta reda på vad innan du kastar ändringarna.

> **Nödutväg:** `git fetch origin main && git reset --hard origin/main` tvingar koden att matcha GitHub. Det är säkert eftersom `data/` är gitignorerad och ospårad — men det åtgärdar bara symptomet, så gör hellre `core.fileMode`-fixen ovan.

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

### Varor eller recept försvann

`data/items.yaml` och `data/recipes/` ignoreras av git och påverkas aldrig av `git pull`. Om filer ändå saknas beror det på ett manuellt misstag (t.ex. `git reset --hard`).

**Återställ från backup:**

```bash
cp /volume1/docker/maltidsplanerare/backups/YYYYMMDD/data/items.yaml \
   /volume1/docker/maltidsplanerare/data/items.yaml
cp /volume1/docker/maltidsplanerare/backups/YYYYMMDD/data/recipes/*.yaml \
   /volume1/docker/maltidsplanerare/data/recipes/
sudo docker compose restart
```

Ersätt `YYYYMMDD` med datumet för din senaste backup.

**Återställ ur git-historiken (om du saknar backup):** Om filerna nyligen var spårade i git men raderats (t.ex. efter en `git reset --hard` eller en merge som tog bort dem) ligger de oftast kvar i historiken. Hämta tillbaka dem från commiten du stod på innan de försvann:

```bash
# Ersätt <commit> med hashen du stod på före raderingen (syns i git reflog)
git checkout <commit> -- data/
git reset HEAD data/      # avstagea — datafilerna ska förbli ignorerade
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

# 2. Backup (rekommenderas)
DATUM=$(date +%Y%m%d)
mkdir -p backups/$DATUM
cp -r data/ backups/$DATUM/

# 3. Hämta ny kod (efter merge på GitHub)
git pull origin main

# 4. Bygg om och starta
sudo docker compose build && sudo docker compose up -d

# 5. Verifiera
sudo docker ps | grep maltidsplanerare
```

---

*Senast uppdaterad: juni 2026*

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
