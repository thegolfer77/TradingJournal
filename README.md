# TradingJournal (Capital.com + Multi-Plattform vorbereitet)

Ein schlankes Trading-Journal mit FastAPI, das:
- Plattform-Konfigurationen speichert (z. B. `capital_com`),
- Trades aus Capital.com synchronisieren kann,
- und eine einfache Web-Oberfläche für Sync + Übersicht bereitstellt.

## TL;DR – in einem Befehl installieren

```bash
curl -fsSL https://raw.githubusercontent.com/thegolfer77/TradingJournal/main/scripts/install.sh | bash
```

Starten:
```bash
cd TradingJournal
source .venv/bin/activate
make run
```

Öffnen: `http://127.0.0.1:8000`

---

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
git checkout main
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
make run
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
