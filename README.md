# TradingJournal (Capital.com + Multi-Plattform vorbereitet)

Ein schlankes Trading-Journal mit FastAPI, das:
- Plattform-Konfigurationen speichert (z. B. `capital_com`),
- Trades aus Capital.com synchronisieren kann,
- und eine einfache Web-Oberfläche für Sync + Übersicht bereitstellt.

## TL;DR – möglichst einfach installieren

### Option A: One-Command Installer (nachdem du dieses Repo auf GitHub gepusht hast)
```bash
curl -fsSL https://raw.githubusercontent.com/<USER>/<REPO>/main/scripts/install.sh | bash -s -- https://github.com/<USER>/<REPO>.git TradingJournal
```

Danach:
```bash
cd TradingJournal
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Option B: Docker (nur Docker nötig)
```bash
docker compose up --build
```

Öffnen: `http://127.0.0.1:8000`

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

## GitHub-Setup für „fertig installieren“
Wenn du möchtest, dass andere nur noch „installieren“ müssen:
1. Repo auf GitHub pushen.
2. In `scripts/install.sh` den Default-Repo-Link anpassen (optional).
3. Optional Tag erstellen (`v0.1.0`) und pushen, damit `docker-publish.yml` ein GHCR-Image baut.
4. Dann können Nutzer entweder:
   - per Installer-Script installieren, oder
   - das fertige Container-Image nutzen.

Die Workflows liegen unter:
- `.github/workflows/ci.yml`
- `.github/workflows/docker-publish.yml`

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
