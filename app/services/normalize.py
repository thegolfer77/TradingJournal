from __future__ import annotations

from dataclasses import dataclass
import hashlib
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


def _first_dict(*values: Any) -> dict[str, Any]:
    for value in values:
        if isinstance(value, dict):
            return value
    return {}


def _pick(source: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in source and source.get(key) is not None:
            return source.get(key)
    return None




def _fallback_trade_id(position: dict[str, Any], row: dict[str, Any], details: dict[str, Any]) -> str:
    raw_key = "|".join(
        [
            str(_pick(position, "epic", "symbol") or _pick(row, "epic", "symbol") or _pick(details, "epic", "symbol") or "UNKNOWN"),
            str(_pick(position, "direction") or _pick(row, "direction") or _pick(details, "direction") or "UNKNOWN"),
            str(_pick(position, "closeDate") or _pick(row, "closeDate", "closedAt", "date", "timestamp", "utcTimestamp") or _pick(details, "closeDate", "closedAt", "date", "timestamp", "utcTimestamp") or ""),
            str(_pick(position, "openDate", "createdDate") or _pick(row, "openDate", "createdAt") or _pick(details, "openDate", "createdAt") or ""),
            str(_pick(position, "profit", "profitAndLoss", "pnl", "profitLoss", "netProfit", "realizedPnl") or _pick(row, "profit", "profitAndLoss", "pnl", "profitLoss", "netProfit", "realizedPnl") or _pick(details, "profit", "profitAndLoss", "pnl", "profitLoss", "netProfit", "realizedPnl") or ""),
            str(_pick(position, "size", "quantity") or _pick(row, "size", "quantity") or _pick(details, "size", "quantity") or ""),
        ]
    )
    digest = hashlib.sha1(raw_key.encode("utf-8")).hexdigest()[:16]
    return f"SYN-{digest}"

def _is_closed(position: dict[str, Any], row: dict[str, Any]) -> bool:
    status_value = str(
        _pick(position, "status")
        or _pick(row, "status", "dealStatus", "statusCode")
        or ""
    ).upper()
    event_type = str(_pick(row, "transactionType", "type", "action", "activityType", "eventType") or "").upper()

    if status_value in {"OPEN", "OPENED", "ACTIVE"}:
        return False

    if _pick(position, "closeDate") or _pick(row, "closeDate", "closedAt"):
        return True

    if status_value in {"CLOSED", "CLOSE", "DELETED", "SETTLED", "ACCEPTED"}:
        return True

    if event_type in {
        "CLOSE",
        "POSITION_CLOSE",
        "POSITION_CLOSED",
        "TRADE_CLOSED",
        "DEAL_CLOSE",
        "CLOSED",
        "DEAL",
        "POSITION_SETTLED",
    }:
        return True

    has_history_date = bool(_pick(row, "date", "timestamp", "utcTimestamp", "createdAt"))
    has_pnl = any(
        _pick(row, key) is not None or _pick(position, key) is not None
        for key in ("profitAndLoss", "profit", "pnl", "profitLoss", "netProfit", "realizedPnl")
    )
    return has_history_date and has_pnl


def normalize_capital_trades(raw_positions: Iterable[dict[str, Any]]) -> list[NormalizedTrade]:
    trades: list[NormalizedTrade] = []
    for row in raw_positions:
        details = _first_dict(row.get("details"), row.get("activity"))
        position = _first_dict(row.get("position"), row.get("deal"), details, row)
        deal = _first_dict(row.get("market"), row.get("instrument"), details.get("market"))

        if not _is_closed(position, row):
            continue

        trade_id = str(
            _pick(position, "dealId", "dealReference")
            or _pick(row, "dealId", "dealReference", "transactionReference", "reference", "id")
            or _pick(details, "dealId", "dealReference", "reference", "id")
            or ""
        )
        if not trade_id:
            trade_id = _fallback_trade_id(position, row, details)

        entry = _to_float(
            _pick(position, "level", "openLevel", "openPrice"),
            _pick(row, "openLevel", "openPrice", "level"),
            _pick(details, "openLevel", "openPrice", "level"),
        )
        exit_price = _to_float(
            _pick(position, "closeLevel", "closePrice"),
            _pick(row, "closeLevel", "closePrice", "level"),
            _pick(details, "closeLevel", "closePrice", "level"),
            default=entry,
        )
        quantity = _to_float(
            _pick(position, "size", "quantity"),
            _pick(row, "size", "quantity"),
            _pick(details, "size", "quantity"),
            default=1.0,
        )
        direction = str(
            _pick(position, "direction")
            or _pick(row, "direction")
            or _pick(details, "direction")
            or "UNKNOWN"
        ).upper()
        pnl = _to_float(
            _pick(position, "profit", "profitAndLoss", "pnl", "profitLoss", "netProfit", "realizedPnl"),
            _pick(row, "profitAndLoss", "profit", "pnl", "profitLoss", "netProfit", "realizedPnl"),
            _pick(details, "profitAndLoss", "profit", "pnl", "profitLoss", "netProfit", "realizedPnl"),
        )

        trades.append(
            NormalizedTrade(
                trade_id=trade_id,
                symbol=str(
                    _pick(deal, "epic")
                    or _pick(position, "epic", "symbol")
                    or _pick(row, "epic", "symbol")
                    or _pick(details, "epic", "symbol")
                    or "UNKNOWN"
                ),
                direction=direction,
                quantity=quantity,
                entry_price=entry,
                exit_price=exit_price,
                pnl=pnl,
                opened_at=_parse_timestamp(
                    _pick(position, "createdDate", "openDate")
                    or _pick(row, "openDate", "date", "timestamp", "utcTimestamp", "createdAt")
                    or _pick(details, "openDate", "date", "timestamp", "utcTimestamp", "createdAt")
                ),
                closed_at=_parse_timestamp(
                    _pick(position, "closeDate")
                    or _pick(row, "closeDate", "closedAt", "date", "timestamp", "utcTimestamp")
                    or _pick(details, "closeDate", "closedAt", "date", "timestamp", "utcTimestamp")
                ),
            )
        )
    return trades
