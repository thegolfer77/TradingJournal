from sqlmodel import Session, select

from app.models import PlatformConfig, Trade
from app.services.capital_api import CapitalComClient
from app.services.normalize import normalize_capital_trades


async def sync_platform_trades(session: Session, platform: PlatformConfig) -> tuple[int, int]:
    if platform.platform_type != "capital_com":
        return 0, 0

    if not platform.api_key or not platform.identifier or not platform.password:
        raise ValueError("Capital.com Plattform ist nicht vollständig konfiguriert.")

    client = CapitalComClient(
        api_key=platform.api_key,
        identifier=platform.identifier,
        password=platform.password,
        demo_mode=platform.demo_mode,
        base_url=platform.api_base_url,
    )
    raw = await client.fetch_closed_positions()
    normalized = normalize_capital_trades(raw)

    imported = 0
    skipped = 0

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
    return imported, skipped
