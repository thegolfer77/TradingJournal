from sqlmodel import Session, select

from app.models import PlatformConfig, Trade
from app.services.capital_api import CapitalComClient
from app.services.normalize import normalize_capital_trades


def _force_closed_rows(raw: list[dict]) -> list[dict]:
    forced: list[dict] = []
    for row in raw:
        patched = dict(row)
        patched.setdefault("status", "CLOSED")
        position = patched.get("position")
        if isinstance(position, dict):
            pos = dict(position)
            pos.setdefault("status", "CLOSED")
            patched["position"] = pos
        forced.append(patched)
    return forced



async def sync_platform_trades(session: Session, platform: PlatformConfig) -> tuple[int, int, int, int, dict[str, int]]:
    if platform.platform_type != "capital_com":
        return 0, 0, 0, 0, {}

    if not platform.api_key or not platform.identifier or not platform.password:
        raise ValueError("Capital.com Plattform ist nicht vollständig konfiguriert.")

    client = CapitalComClient(
        api_key=platform.api_key,
        identifier=platform.identifier,
        password=platform.password,
        base_url=platform.api_base_url,
    )
    debug = await client.fetch_closed_positions_debug()
    source_counts = {k: int(v.get("rows", 0)) for k, v in debug.get("sources", {}).items() if isinstance(v, dict)}

    raw = await client.fetch_closed_positions()
    normalized = normalize_capital_trades(raw)
    if len(raw) > 0 and len(normalized) == 0:
        normalized = normalize_capital_trades(_force_closed_rows(raw))

    imported = 0
    skipped = 0
    fetched = len(raw)
    normalized_count = len(normalized)

    for trade in normalized:
        existing = session.exec(
            select(Trade).where(
                Trade.platform_id == platform.id,
                Trade.external_trade_id == trade.trade_id,
            )
        ).first()
        if existing:
            skipped += 1
            continue

        session.add(
            Trade(
                platform_id=platform.id,
                external_trade_id=trade.trade_id,
                symbol=trade.symbol,
                direction=trade.direction,
                quantity=trade.quantity,
                entry_price=trade.entry_price,
                exit_price=trade.exit_price,
                pnl=trade.pnl,
                opened_at=trade.opened_at,
                closed_at=trade.closed_at,
            )
        )
        imported += 1

    session.commit()
    return imported, skipped, fetched, normalized_count, source_counts
