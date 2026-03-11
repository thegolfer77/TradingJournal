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


def _to_float(*values: Any, default: float = 0.0) -> float:
    for value in values:
        if value is None:
            continue
        try:
            return float(value)
        except (TypeError, ValueError):
            continue
    return default


def _is_closed(position: dict[str, Any], row: dict[str, Any]) -> bool:
    status_value = str(
        position.get("status")
        or row.get("status")
        or row.get("dealStatus")
        or row.get("statusCode")
        or ""
    ).upper()
    tx_type = str(row.get("transactionType") or row.get("type") or row.get("action") or "").upper()

    if status_value in {"OPEN", "OPENED", "ACTIVE"}:
        return False

    if position.get("closeDate") or row.get("closeDate"):
        return True

    if status_value in {"CLOSED", "CLOSE", "DELETED", "SETTLED", "ACCEPTED"}:
        return True

    if tx_type in {
        "CLOSE",
        "POSITION_CLOSE",
        "POSITION_CLOSED",
        "TRADE_CLOSED",
        "DEAL_CLOSE",
        "CLOSED",
        "DEAL",
    }:
        return True

    # Some history endpoints only include transaction + pnl without explicit closed marker.
    has_history_date = bool(row.get("date") or row.get("timestamp") or row.get("utcTimestamp"))
    has_pnl = any(
        key in row or key in position
        for key in ("profitAndLoss", "profit", "pnl", "profitLoss")
    )
    return has_history_date and has_pnl


def normalize_capital_trades(raw_positions: Iterable[dict[str, Any]]) -> list[NormalizedTrade]:
    trades: list[NormalizedTrade] = []
    for row in raw_positions:
        position = row.get("position", row)
        deal = row.get("market", row.get("instrument", {}))

        if not _is_closed(position, row):
            continue

        trade_id = str(
            position.get("dealId")
            or position.get("dealReference")
            or row.get("dealId")
            or row.get("dealReference")
            or row.get("transactionReference")
            or row.get("reference")
            or row.get("id")
            or ""
        )
        if not trade_id:
            continue

        entry = _to_float(
            position.get("level"),
            position.get("openLevel"),
            position.get("openPrice"),
            row.get("openLevel"),
            row.get("openPrice"),
        )
        exit_price = _to_float(
            position.get("closeLevel"),
            position.get("closePrice"),
            row.get("closeLevel"),
            row.get("closePrice"),
            row.get("level"),
            default=entry,
        )
        quantity = _to_float(
            position.get("size"),
            position.get("quantity"),
            row.get("size"),
            row.get("quantity"),
            default=1.0,
        )
        direction = str(position.get("direction") or row.get("direction") or "UNKNOWN").upper()
        pnl = _to_float(
            position.get("profit"),
            position.get("profitAndLoss"),
            position.get("pnl"),
            position.get("profitLoss"),
            row.get("profitAndLoss"),
            row.get("profit"),
            row.get("pnl"),
            row.get("profitLoss"),
        )

        trades.append(
            NormalizedTrade(
                trade_id=trade_id,
                symbol=str(deal.get("epic") or position.get("epic") or row.get("epic") or row.get("symbol") or "UNKNOWN"),
                direction=direction,
                quantity=quantity,
                entry_price=entry,
                exit_price=exit_price,
                pnl=pnl,
                opened_at=_parse_timestamp(
                    position.get("createdDate")
                    or position.get("openDate")
                    or row.get("openDate")
                    or row.get("date")
                    or row.get("timestamp")
                    or row.get("utcTimestamp")
                ),
                closed_at=_parse_timestamp(
                    position.get("closeDate")
                    or row.get("closeDate")
                    or row.get("date")
                    or row.get("timestamp")
                    or row.get("utcTimestamp")
                ),
            )
        )
    return trades
