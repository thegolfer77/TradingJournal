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


def _num(*values: Any) -> float:
    for v in values:
        if v is None:
            continue
        try:
            return float(v)
        except (TypeError, ValueError):
            continue
    return 0.0


class CapitalComClient:
    """Minimal Capital.com API client focused on trade history sync."""

    def __init__(
        self,
        api_key: str,
        identifier: str,
        password: str,
        demo_mode: bool = False,
        base_url: str | None = None,
    ) -> None:
        self.api_key = api_key
        self.identifier = identifier
        self.password = password
        self.base_url = base_url or "https://api-capital.backend-capital.com/api/v1"

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

    async def _try_get(self, path: str, headers: dict[str, str], params: dict[str, Any] | None = None) -> Any:
        try:
            return await self._get(path, headers, params)
        except httpx.HTTPStatusError:
            return None

    def _extract_rows(self, payload: Any) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []

        def walk(node: Any) -> None:
            if isinstance(node, list):
                for item in node:
                    walk(item)
                return
            if not isinstance(node, dict):
                return

            looks_trade_like = any(
                key in node
                for key in (
                    "position",
                    "deal",
                    "dealId",
                    "dealReference",
                    "transactionReference",
                    "profitAndLoss",
                    "profit",
                    "pnl",
                    "activityType",
                )
            )
            if looks_trade_like:
                rows.append(node)

            for value in node.values():
                walk(value)

        walk(payload)
        return rows


    async def _collect_paginated(self, path: str, headers: dict[str, str], base_params: dict[str, Any], max_pages: int = 15) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for page in range(1, max_pages + 1):
            params = dict(base_params)
            params.setdefault("pageNumber", page)
            payload = await self._try_get(path, headers, params)
            if not payload:
                break
            page_rows = self._extract_rows(payload)
            if not page_rows:
                break
            rows.extend(page_rows)

            # Stop if payload exposes paging meta and says last page.
            if isinstance(payload, dict):
                meta = payload.get("metadata") or payload.get("paging") or {}
                if isinstance(meta, dict):
                    total_pages = meta.get("totalPages") or meta.get("pageCount")
                    if isinstance(total_pages, int) and page >= total_pages:
                        break
        return rows

    async def fetch_closed_positions(self, limit: int = 1000) -> list[dict[str, Any]]:
        headers = await self._auth_headers()
        try:
            endpoints = [
                ("/positions", {"status": "CLOSED", "limit": limit, "max": limit, "pageSize": limit}),
                ("/positions", {"limit": limit, "max": limit, "pageSize": limit}),
                ("/history/positions", {"limit": limit, "max": limit, "pageSize": limit}),
                ("/history/transactions", {"limit": limit, "max": limit, "pageSize": limit}),
                ("/history/activity", {"limit": limit, "max": limit, "pageSize": limit}),
                ("/history/deals", {"limit": limit, "max": limit, "pageSize": limit}),
                ("/history", {"limit": limit, "max": limit, "pageSize": limit}),
                ("/history/activities", {"limit": limit, "max": limit, "pageSize": limit}),
            ]

            rows: list[dict[str, Any]] = []
            source_counts: dict[str, int] = {}
            for path, params in endpoints:
                page_rows = await self._collect_paginated(path, headers, params)
                key = path if "status" not in params else f"{path}?status={params['status']}"
                source_counts[key] = source_counts.get(key, 0) + len(page_rows)
                for row in page_rows:
                    tagged = dict(row)
                    tagged.setdefault("_source", key)
                    rows.append(tagged)

            unique_rows: list[dict[str, Any]] = []
            seen: set[str] = set()
            for row in rows:
                key = str(
                    row.get("dealId")
                    or row.get("dealReference")
                    or row.get("transactionReference")
                    or row.get("reference")
                    or row.get("id")
                    or repr(row)
                )
                if key in seen:
                    continue
                seen.add(key)
                unique_rows.append(row)

            return unique_rows
        except httpx.HTTPStatusError as exc:
            raise self._map_http_error(exc) from exc
        except httpx.HTTPError as exc:
            raise CapitalAPIError("Netzwerkfehler beim Abruf der Positionen.", status_code=502) from exc


    async def fetch_closed_positions_debug(self, limit: int = 1000) -> dict[str, Any]:
        headers = await self._auth_headers()
        endpoints = [
            ("/positions", {"status": "CLOSED", "limit": limit, "max": limit, "pageSize": limit}),
            ("/positions", {"limit": limit, "max": limit, "pageSize": limit}),
            ("/history/positions", {"limit": limit, "max": limit, "pageSize": limit}),
            ("/history/transactions", {"limit": limit, "max": limit, "pageSize": limit}),
            ("/history/activity", {"limit": limit, "max": limit, "pageSize": limit}),
            ("/history/deals", {"limit": limit, "max": limit, "pageSize": limit}),
            ("/history", {"limit": limit, "max": limit, "pageSize": limit}),
            ("/history/activities", {"limit": limit, "max": limit, "pageSize": limit}),
        ]
        out: dict[str, Any] = {"sources": {}}
        for path, params in endpoints:
            key = path if "status" not in params else f"{path}?status={params['status']}"
            payload = await self._try_get(path, headers, params)
            if payload is None:
                out["sources"][key] = {"available": False, "rows": 0}
                continue
            rows = self._extract_rows(payload)
            out["sources"][key] = {"available": True, "rows": len(rows)}
        return out

    async def fetch_open_positions(self, limit: int = 200) -> list[OpenPosition]:
        headers = await self._auth_headers()
        try:
            endpoints = [
                ("/positions", {"status": "OPEN", "limit": limit, "max": limit, "pageSize": limit}),
                ("/positions", {"limit": limit, "max": limit, "pageSize": limit}),
            ]

            rows: list[dict[str, Any]] = []
            for path, params in endpoints:
                rows.extend(await self._collect_paginated(path, headers, params, max_pages=10))

            result: list[OpenPosition] = []
            seen_ids: set[str] = set()
            for row in rows:
                position = row.get("position", row)
                status = str(position.get("status") or row.get("status") or "").upper()
                if status and status not in {"OPEN", "OPENED", "ACTIVE"}:
                    continue

                market = row.get("market", {})
                position_id = str(position.get("dealId") or position.get("dealReference") or "")
                if not position_id:
                    position_id = f"OPEN-{str(position.get('epic') or row.get('epic') or 'UNKNOWN')}-{str(position.get('openDate') or position.get('createdDate') or row.get('date') or '')}"

                if position_id in seen_ids:
                    continue
                seen_ids.add(position_id)

                current_price = _num(
                    market.get("bid"),
                    market.get("offer"),
                    position.get("bid"),
                    position.get("offer"),
                    position.get("currentPrice"),
                )
                unrealized = _num(
                    position.get("profit"),
                    position.get("profitAndLoss"),
                    position.get("upl"),
                    position.get("pnl"),
                    position.get("profitLoss"),
                    row.get("profitAndLoss"),
                    row.get("upl"),
                    row.get("pnl"),
                    row.get("profitLoss"),
                )
                result.append(
                    OpenPosition(
                        position_id=position_id,
                        symbol=str(market.get("epic") or position.get("epic") or "UNKNOWN"),
                        direction=str(position.get("direction") or "UNKNOWN").upper(),
                        quantity=_num(position.get("size"), position.get("quantity")),
                        entry_price=_num(position.get("level"), position.get("openLevel"), position.get("openPrice")),
                        current_price=current_price,
                        unrealized_pnl=unrealized,
                        opened_at=_parse_timestamp(position.get("createdDate") or position.get("openDate")),
                    )
                )
            return result
        except httpx.HTTPStatusError as exc:
            raise self._map_http_error(exc) from exc
        except httpx.HTTPError as exc:
            raise CapitalAPIError("Netzwerkfehler beim Abruf offener Positionen.", status_code=502) from exc
