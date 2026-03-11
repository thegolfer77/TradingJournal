from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

import httpx


@dataclass
class CapitalAPIError(Exception):
    message: str
    status_code: int = 400


@dataclass
class OpenPosition:
    position_id: str
    symbol: str
    direction: str
    quantity: float
    entry_price: float
    current_price: float
    unrealized_pnl: float
    opened_at: datetime


def _extract_error_code(response: httpx.Response) -> str:
    try:
        payload = response.json()
        if isinstance(payload, dict):
            return str(payload.get("errorCode") or payload.get("message") or "")
    except Exception:
        pass
    return ""


def _parse_timestamp(value: str | None) -> datetime:
    if not value:
        return datetime.utcnow()
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


class CapitalComClient:
    """Minimal Capital.com API client focused on trade history sync."""

    def __init__(
        self,
        api_key: str,
        identifier: str,
        password: str,
        demo_mode: bool = True,
        base_url: str | None = None,
    ) -> None:
        self.api_key = api_key
        self.identifier = identifier
        self.password = password
        self.base_url = base_url or (
            "https://demo-api-capital.backend-capital.com/api/v1"
            if demo_mode
            else "https://api-capital.backend-capital.com/api/v1"
        )

    @staticmethod
    def _map_http_error(exc: httpx.HTTPStatusError) -> CapitalAPIError:
        code = exc.response.status_code
        api_reason = _extract_error_code(exc.response)
        suffix = f" API-Reason: {api_reason}" if api_reason else ""
        if code == 401:
            return CapitalAPIError(
                "Capital.com Login fehlgeschlagen (401). Prüfe API-Key, Identifier, Passwort, ob Demo/Live korrekt gesetzt ist und ob der API-Key für dieses Konto freigeschaltet ist." + suffix,
                status_code=401,
            )
        if code == 429:
            return CapitalAPIError(
                "Capital.com Rate Limit erreicht (429). Bitte 30-60 Sekunden warten und erneut synchronisieren." + suffix,
                status_code=429,
            )
        return CapitalAPIError(
            f"Capital.com API Fehler ({code}). Bitte später erneut versuchen." + suffix,
            status_code=400,
        )

    async def _auth_headers(self) -> dict[str, str]:
        try:
            async with httpx.AsyncClient(timeout=20) as client:
                response = await client.post(
                    f"{self.base_url}/session",
                    headers={
                        "X-CAP-API-KEY": self.api_key,
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                    },
                    json={"identifier": self.identifier, "password": self.password},
                )
                response.raise_for_status()
                cst = response.headers.get("CST", "")
                security_token = response.headers.get("X-SECURITY-TOKEN", "")
                return {
                    "X-CAP-API-KEY": self.api_key,
                    "CST": cst,
                    "X-SECURITY-TOKEN": security_token,
                }
        except httpx.HTTPStatusError as exc:
            raise self._map_http_error(exc) from exc
        except httpx.HTTPError as exc:
            raise CapitalAPIError("Netzwerkfehler bei Capital.com. Bitte Verbindung prüfen.", status_code=502) from exc

    async def _get(self, path: str, headers: dict[str, str], params: dict[str, Any] | None = None) -> Any:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(f"{self.base_url}{path}", headers=headers, params=params)
            response.raise_for_status()
            return response.json()

    async def fetch_closed_positions(self, limit: int = 200) -> list[dict[str, Any]]:
        headers = await self._auth_headers()
        try:
            payload = await self._get("/positions", headers, {"status": "CLOSED", "limit": limit})
            positions = payload.get("positions", payload if isinstance(payload, list) else [])

            if not positions:
                hist = await self._get("/history/positions", headers, {"limit": limit})
                positions = hist.get("positions", hist.get("deals", hist if isinstance(hist, list) else []))

            if not positions:
                tx = await self._get("/history/transactions", headers, {"limit": limit})
                positions = tx.get("transactions", tx.get("deals", tx if isinstance(tx, list) else []))

            return positions
        except httpx.HTTPStatusError as exc:
            raise self._map_http_error(exc) from exc
        except httpx.HTTPError as exc:
            raise CapitalAPIError("Netzwerkfehler beim Abruf der Positionen.", status_code=502) from exc

    async def fetch_open_positions(self, limit: int = 200) -> list[OpenPosition]:
        headers = await self._auth_headers()
        try:
            payload = await self._get("/positions", headers, {"status": "OPEN", "limit": limit})
            rows = payload.get("positions", payload if isinstance(payload, list) else [])
            result: list[OpenPosition] = []
            for row in rows:
                position = row.get("position", row)
                market = row.get("market", {})
                result.append(
                    OpenPosition(
                        position_id=str(position.get("dealId") or position.get("dealReference") or ""),
                        symbol=str(market.get("epic") or position.get("epic") or "UNKNOWN"),
                        direction=str(position.get("direction") or "UNKNOWN").upper(),
                        quantity=float(position.get("size") or 0),
                        entry_price=float(position.get("level") or position.get("openLevel") or 0),
                        current_price=float(position.get("bid") or position.get("offer") or position.get("currentPrice") or 0),
                        unrealized_pnl=float(position.get("profit") or position.get("profitAndLoss") or 0),
                        opened_at=_parse_timestamp(position.get("createdDate") or position.get("openDate")),
                    )
                )
            return result
        except httpx.HTTPStatusError as exc:
            raise self._map_http_error(exc) from exc
        except httpx.HTTPError as exc:
            raise CapitalAPIError("Netzwerkfehler beim Abruf offener Positionen.", status_code=502) from exc
