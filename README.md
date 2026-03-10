# TradingJournal (Capital.com + Multi-Plattform vorbereitet)

Ein schlankes Trading-Journal mit FastAPI, das:
- Plattform-Konfigurationen speichert (z. B. `capital_com`),
- Trades aus Capital.com synchronisieren kann,
- und eine einfache Web-Oberfläche für Sync + Übersicht bereitstellt.

## Schnellstart (robust)

```bash
git clone https://github.com/thegolfer77/TradingJournal.git
cd TradingJournal
bash install.sh
bash run.sh
```

Öffnen: `http://127.0.0.1:8000`

## Wenn bei dir steht: `requirements.txt: No such file or directory`
Das heißt: Du bist in einem falschen Ordner/Branch-Stand.

Prüfen:
```bash
pwd
ls
bash doctor.sh
```

Neu und sauber starten:
```bash
cd ~
rm -rf TradingJournal
git clone https://github.com/thegolfer77/TradingJournal.git
cd TradingJournal
bash install.sh
bash run.sh
```

## Manueller Fallback ohne Scripts
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Alternativ: Docker
```bash
docker compose up --build
```
