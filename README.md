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

## Installation & Start (lokal)

### 1) Voraussetzungen
- Python **3.11+**
- `pip`

### 2) Installation
```bash
git clone <dein-repo-url>
cd TradingJournal
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Alternativ mit Makefile:
```bash
make setup
```

### 3) App starten
```bash
source .venv/bin/activate
uvicorn app.main:app --reload
```

Alternativ mit Makefile:
```bash
make run
```

### 4) Im Browser öffnen
- UI: `http://127.0.0.1:8000`
- API-Doku (Swagger): `http://127.0.0.1:8000/docs`

## Installation & Start (Docker)

### Mit Docker Compose
```bash
docker compose up --build
```

Danach öffnen:
- UI: `http://127.0.0.1:8000`
- API-Doku: `http://127.0.0.1:8000/docs`

## So benutzt du das Journal
1. Öffne die Startseite.
2. Unter **Plattform hinzufügen** eine Plattform anlegen:
   - `platform_type = capital_com`
   - `api_key`, `identifier`, `password` eintragen
   - `demo_mode` aktiviert lassen für Demo-Account
3. Speichern.
4. Bei der Plattform auf **Sync** klicken.
5. Importierte Trades werden in der Tabelle angezeigt.

## API Endpunkte
- `POST /api/platforms` Plattform speichern
- `GET /api/platforms` Plattformen auflisten
- `POST /api/platforms/{id}/sync` Trades synchronisieren
- `GET /api/trades` Trades auflisten

## Capital.com Hinweise
- Für Live statt Demo in der Plattformkonfiguration `demo_mode=false` setzen.
- Optional `api_base_url` setzen, falls du einen abweichenden Endpoint nutzen willst.
- Die API kann je nach Konto/Region Felder leicht unterschiedlich liefern; Mapping erfolgt in `normalize_capital_trades`.

## Fehlerbehebung
- **`pip install` schlägt fehl**: Prüfe Proxy/Firewall/Netzwerkzugriff.
- **`ModuleNotFoundError`**: Virtuelle Umgebung aktivieren (`source .venv/bin/activate`) und Requirements erneut installieren.
- **Port 8000 belegt**: Starte mit anderem Port, z. B. `uvicorn app.main:app --reload --port 8010`.

## Roadmap Richtung "ähnlich TradeZella"
- Tagging/Setups, Journaling-Notizen pro Trade
- Metriken (Winrate, Avg R-Multiple, Drawdown)
- Charts/Equity-Kurve
- Weitere Broker-Connectoren (Bybit, Binance, MT5, etc.)
