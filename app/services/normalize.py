from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Iterable


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
