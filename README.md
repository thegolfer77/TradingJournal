# TradingJournal (Capital.com + Multi-Plattform vorbereitet)

Ein schlankes Trading-Journal mit FastAPI, das:
- Plattform-Konfigurationen speichert (z. B. `capital_com`),
- Trades aus Capital.com synchronisieren kann,
- und eine einfache Web-Oberfläche für Sync + Übersicht bereitstellt.

## TL;DR – in einem Befehl installieren (ohne Raw-URL)

```bash
git clone https://github.com/thegolfer77/TradingJournal.git && cd TradingJournal && bash scripts/install.sh
```

## Starten (3 Befehle)
```bash
cd ~/TradingJournal
source .venv/bin/activate
bash scripts/run.sh
```

Öffnen: `http://127.0.0.1:8000`

---

## Warum bei dir `curl ... install.sh` mit 404 endete
Die alte Raw-URL war auf einen festen Branch (`main`) verdrahtet. Wenn der Branch anders heißt, kommt 404.
Darum ist der neue empfohlene Weg: **clone + lokales Script starten** (oben), branch-unabhängig.

## Wenn `make run` fehlschlägt
Nutze stattdessen immer:
```bash
bash scripts/run.sh
```

## Warum bei dir Fehler kamen (`requirements.txt` fehlt, `No module named app`)
Das bedeutet fast immer: Du bist **nicht im richtigen Projektstand/Branch** oder in einem falschen Ordner.

Sofort-Check:
```bash
cd ~/TradingJournal
bash scripts/doctor.sh
```

Falls Dateien fehlen:
```bash
cd ~
rm -rf TradingJournal
git clone https://github.com/thegolfer77/TradingJournal.git
cd TradingJournal
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
bash scripts/run.sh
```

## Alternativ: Docker
```bash
docker compose up --build
```

## Features
- **Plattform-Management**: mehrere Konten/Plattformen konfigurierbar.
- **Capital.com Integration**: Login via `API Key + Identifier + Passwort`, Import von geschlossenen Positionen.
- **Trade-Übersicht**: gespeicherte Trades aus SQLite.
- **Erweiterbar**: `platform_type=generic_rest` ist als Platzhalter für weitere APIs angelegt.

## API Endpunkte
- `POST /api/platforms` Plattform speichern
- `GET /api/platforms` Plattformen auflisten
- `POST /api/platforms/{id}/sync` Trades synchronisieren
- `GET /api/trades` Trades auflisten
