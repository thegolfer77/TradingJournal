# TradingJournal (Capital.com + Multi-Plattform vorbereitet)

Ein schlankes Trading-Journal mit FastAPI, das:
- Plattform-Konfigurationen speichert (z. B. `capital_com`),
- Trades aus Capital.com synchronisieren kann,
- und eine einfache Web-Oberfläche für Sync + Übersicht bereitstellt.

## TL;DR – funktioniert auch ohne `install.sh`

```bash
git clone https://github.com/thegolfer77/TradingJournal.git
cd TradingJournal
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Öffnen: `http://127.0.0.1:8000`

## Komfort-Variante (wenn vorhanden)
```bash
bash install.sh
bash run.sh
```

---

## Wenn `install.sh` fehlt
Dann bist du auf einem älteren Stand ohne Root-Skripte. Nutze einfach den manuellen Weg oben (python venv + pip + uvicorn).

## Diagnose
```bash
cd ~/TradingJournal
[ -f install.sh ] && echo "install.sh vorhanden" || echo "install.sh fehlt"
[ -f requirements.txt ] && echo "requirements.txt vorhanden" || echo "requirements.txt fehlt"
[ -d app ] && echo "app/ vorhanden" || echo "app/ fehlt"
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
