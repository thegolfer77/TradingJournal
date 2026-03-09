from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Iterable

import httpx


@dataclass
class NormalizedTrade:
    trade_id: str
    symbol: str
    direction: str
    quantity: float
    entry_price: float
    exit_price: float
    pnl: float
    opened_at: datetime
    closed_at: datetime


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

    async def _auth_headers(self) -> dict[str, str]:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                f"{self.base_url}/session",
                headers={"X-CAP-API-KEY": self.api_key},
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

    async def fetch_closed_positions(self, limit: int = 200) -> list[dict[str, Any]]:
        headers = await self._auth_headers()
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(
                f"{self.base_url}/positions",
                headers=headers,
                params={"status": "CLOSED", "limit": limit},
            )
            response.raise_for_status()
            payload = response.json()
            return payload.get("positions", payload if isinstance(payload, list) else [])


def _parse_timestamp(value: str | None) -> datetime:
    if not value:
        return datetime.utcnow()
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def normalize_capital_trades(raw_positions: Iterable[dict[str, Any]]) -> list[NormalizedTrade]:
    trades: list[NormalizedTrade] = []
    for row in raw_positions:
        position = row.get("position", row)
        deal = row.get("market", {})

        trade_id = str(position.get("dealId") or position.get("dealReference") or "")
        if not trade_id:
            continue

        entry = float(position.get("level") or 0)
        exit_price = float(position.get("closeLevel") or entry)
        quantity = float(position.get("size") or 0)
        direction = str(position.get("direction") or "UNKNOWN").upper()
        pnl = float(position.get("profit") or 0)

        trades.append(
            NormalizedTrade(
                trade_id=trade_id,
                symbol=str(deal.get("epic") or position.get("epic") or "UNKNOWN"),
                direction=direction,
                quantity=quantity,
                entry_price=entry,
                exit_price=exit_price,
                pnl=pnl,
                opened_at=_parse_timestamp(position.get("createdDate")),
                closed_at=_parse_timestamp(position.get("closeDate")),
            )
        )
    return trades
