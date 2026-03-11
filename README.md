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
6. Sync-Button klicken (importiert geschlossene Trades)

## Fehler 401 / 429 beim Sync
- **401**: Zugangsdaten passen nicht zum Modus (Demo vs Live), API-Key nicht für dieses Konto freigeschaltet, Identifier/Passwort falsch oder Session-Scope nicht korrekt.
- **429**: Rate Limit. 30-60 Sekunden warten und erneut synchronisieren.
- Die API-Fehlermeldung (`errorCode`) wird jetzt direkt in der UI angezeigt (als `API-Reason`), damit klar ist, woran es liegt.

### Wenn 401 trotz korrekter Daten bleibt
- Prüfen, ob der API-Key wirklich für **Live** erzeugt wurde (nicht Demo-Key).
- In Capital.com prüfen, ob API-Zugriff für das Konto aktiv ist.
- Identifier exakt wie im Capital-Login verwenden (Groß/Kleinschreibung beachten).
- 2FA-/Sicherheits-Policy im Konto prüfen.
- Bei wiederholten Fehlversuchen 1-2 Minuten warten (temporärer Block möglich).

Hinweis: Der Sync importiert jetzt ausschließlich geschlossene Trades (keine offenen Positionen).

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


## Sync-Debug
Nach dem Sync zeigt die UI jetzt: `fetched`, `normalized`, `importiert`, `übersprungen`.
- `fetched=0`: Capital liefert keine Historie zurück (Endpoint/Konto-Policy prüfen).
- `fetched>0` aber `normalized=0`: Payload hat keine als geschlossen erkannten Trades.


## Alte offene Positionen bereinigen
Wenn früher offene Positionen importiert wurden, bleiben sie in der lokalen SQLite-DB.
Für einen sauberen Neuaufbau:
```bash
rm -f trading_journal.db
python -m uvicorn app.main:app --reload
```
Danach erneut Sync ausführen.
