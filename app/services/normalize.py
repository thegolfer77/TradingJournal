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


def _is_closed(position: dict[str, Any], row: dict[str, Any]) -> bool:
    status_value = str(position.get("status") or row.get("status") or "").upper()
    if status_value in {"OPEN", "OPENED"}:
        return False
    if status_value:
        return True
    if position.get("closeDate") or position.get("closeLevel"):
        return True
    if position.get("profitAndLoss") is not None and (position.get("openDate") or row.get("date")):
        return True
    return False


def normalize_capital_trades(raw_positions: Iterable[dict[str, Any]]) -> list[NormalizedTrade]:
    trades: list[NormalizedTrade] = []
    for row in raw_positions:
        position = row.get("position", row)
        deal = row.get("market", {})

        if not _is_closed(position, row):
            continue

        trade_id = str(
            position.get("dealId")
            or position.get("dealReference")
            or row.get("transactionReference")
            or row.get("reference")
            or ""
        )
        if not trade_id:
            continue

        entry = float(position.get("level") or position.get("openLevel") or position.get("openPrice") or 0)
        exit_price = float(position.get("closeLevel") or position.get("closePrice") or entry)
        quantity = float(position.get("size") or position.get("quantity") or 0)
        direction = str(position.get("direction") or row.get("direction") or "UNKNOWN").upper()
        pnl = float(position.get("profit") or position.get("profitAndLoss") or row.get("profitAndLoss") or 0)

        trades.append(
            NormalizedTrade(
                trade_id=trade_id,
                symbol=str(deal.get("epic") or position.get("epic") or row.get("epic") or "UNKNOWN"),
                direction=direction,
                quantity=quantity,
                entry_price=entry,
                exit_price=exit_price,
                pnl=pnl,
                opened_at=_parse_timestamp(position.get("createdDate") or position.get("openDate") or row.get("date")),
                closed_at=_parse_timestamp(position.get("closeDate") or row.get("date")),
            )
        )
    return trades
