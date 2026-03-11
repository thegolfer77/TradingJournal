# TradingJournal (Capital.com + Multi-Plattform vorbereitet)

Ein schlankes Trading-Journal mit FastAPI, das:
- Plattform-Konfigurationen speichert (z. B. `capital_com`),
- Trades aus Capital.com synchronisieren kann,
- und eine einfache Web-Oberfläche für Sync + Übersicht bereitstellt.

## Schnellstart (normal)

```bash
git clone https://github.com/thegolfer77/TradingJournal.git
cd TradingJournal
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Öffnen: `http://127.0.0.1:8000`

## Wenn bei dir steht: `requirements.txt` / `install.sh` / `run.sh` fehlt
Dann ist sehr wahrscheinlich ein falscher Branch ausgecheckt.

### 1) Auto-Recovery ausführen
```bash
cd ~/TradingJournal
bash recover.sh
```

### 2) Danach normal installieren
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

## Manuelle Diagnose
```bash
cd ~/TradingJournal
git branch -a
git rev-parse --abbrev-ref HEAD
git ls-tree --name-only HEAD
```
Wenn dort weder `requirements.txt` noch `app/` auftaucht, ist der falsche Branch aktiv.

## Alternativ: Docker
```bash
docker compose up --build
```
