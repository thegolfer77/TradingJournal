# TradingJournal (Capital.com + Multi-Plattform vorbereitet)

## Start
```bash
git clone https://github.com/thegolfer77/TradingJournal.git
cd TradingJournal
git checkout -B codex/erstelle-tradingjournal-mit-api-zugriff origin/codex/erstelle-tradingjournal-mit-api-zugriff
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

## Live-Konto synchronisieren (Capital.com)
1. Plattform hinzufügen
2. `platform_type = capital_com`
3. API Key + Identifier + Passwort eintragen
4. **Demo-Modus deaktivieren** (wichtig für Live)
5. Optional `api_base_url` setzen
6. Sync-Button klicken

## Neue Auswertungen
- Kalenderansicht mit Tages-/Monats-/Jahresaggregation
- Gewinn in Geld
- Gewinn in %
- Anzahl Trades
- % Gewinntrades
- Profit Faktor

## API
- `GET /api/stats?period=day|month|year`
- `POST /api/platforms/{id}/sync`
- `GET /api/trades`
