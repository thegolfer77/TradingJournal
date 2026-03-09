# TradingJournal (Capital.com + Multi-Plattform vorbereitet)

Ein schlankes Trading-Journal mit FastAPI, das:
- Plattform-Konfigurationen speichert (z. B. `capital_com`),
- Trades aus Capital.com synchronisieren kann,
- und eine einfache Web-Oberfläche für Sync + Übersicht bereitstellt.

## Features
- **Plattform-Management**: mehrere Konten/Plattformen konfigurierbar.
- **Capital.com Integration**: Login via `API Key + Identifier + Passwort`, Import von geschlossenen Positionen.
- **Trade-Übersicht**: gespeicherte Trades aus SQLite.
- **Erweiterbar**: `platform_type=generic_rest` ist als Platzhalter für weitere APIs angelegt.

## Schnellstart
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Dann öffnen: `http://127.0.0.1:8000`

## API Endpunkte
- `POST /api/platforms` Plattform speichern
- `GET /api/platforms` Plattformen auflisten
- `POST /api/platforms/{id}/sync` Trades synchronisieren
- `GET /api/trades` Trades auflisten

## Capital.com Hinweise
- Für Live statt Demo in der Plattformkonfiguration `demo_mode=false` setzen.
- Optional `api_base_url` setzen, falls du einen abweichenden Endpoint nutzen willst.
- Die API kann je nach Konto/Region Felder leicht unterschiedlich liefern; Mapping erfolgt in `normalize_capital_trades`.

## Roadmap Richtung "ähnlich TradeZella"
- Tagging/Setups, Journaling-Notizen pro Trade
- Metriken (Winrate, Avg R-Multiple, Drawdown)
- Charts/Equity-Kurve
- Weitere Broker-Connectoren (Bybit, Binance, MT5, etc.)
