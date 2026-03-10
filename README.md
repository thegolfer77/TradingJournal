# TradingJournal (Capital.com + Multi-Plattform vorbereitet)

Ein schlankes Trading-Journal mit FastAPI, das:
- Plattform-Konfigurationen speichert (z. B. `capital_com`),
- Trades aus Capital.com synchronisieren kann,
- und eine einfache Web-Oberfläche für Sync + Übersicht bereitstellt.

## TL;DR – robust installieren

```bash
git clone https://github.com/thegolfer77/TradingJournal.git
cd TradingJournal
bash install.sh
```

## Starten (3 Befehle)
```bash
cd ~/TradingJournal
source .venv/bin/activate
bash run.sh
```

Öffnen: `http://127.0.0.1:8000`

---

## Warum bei dir `scripts/install.sh`/`scripts/run.sh` fehlten
Du warst auf einem Stand/Branch, in dem `scripts/` nicht vorhanden war.
Darum gibt es jetzt **Root-Fallbacks** (`install.sh`, `run.sh`, `doctor.sh`), die auch ohne `scripts/` funktionieren.

## Diagnose
```bash
cd ~/TradingJournal
bash doctor.sh
```

## Falls weiterhin etwas fehlt
```bash
cd ~
rm -rf TradingJournal
git clone https://github.com/thegolfer77/TradingJournal.git
cd TradingJournal
bash install.sh
bash run.sh
```

## Alternativ: Docker
```bash
docker compose up --build
```

## API Endpunkte
- `POST /api/platforms`
- `GET /api/platforms`
- `POST /api/platforms/{id}/sync`
- `GET /api/trades`
