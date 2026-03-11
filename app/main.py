from collections import defaultdict
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from app.db import get_session, init_db
from app.models import PlatformConfig, Trade
from app.schemas import PeriodStats, PlatformCreate, PlatformRead, SyncResult, TradeRead
from app.services.capital_api import CapitalAPIError
from app.services.sync import sync_platform_trades

app = FastAPI(title="TradingJournal", version="0.1.0")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/platforms", response_model=PlatformRead)
def create_platform(payload: PlatformCreate, session: Session = Depends(get_session)):
    existing = session.exec(select(PlatformConfig).where(PlatformConfig.name == payload.name)).first()
    if existing:
        raise HTTPException(status_code=409, detail="Name ist bereits vergeben")

    row = PlatformConfig(**payload.model_dump())
    session.add(row)
    session.commit()
    session.refresh(row)
    return row


@app.get("/api/platforms", response_model=list[PlatformRead])
def list_platforms(session: Session = Depends(get_session)):
    rows = session.exec(select(PlatformConfig)).all()
    return rows


@app.post("/api/platforms/{platform_id}/sync", response_model=SyncResult)
async def sync_platform(platform_id: int, session: Session = Depends(get_session)):
    platform = session.get(PlatformConfig, platform_id)
    if not platform:
        raise HTTPException(status_code=404, detail="Plattform nicht gefunden")
    try:
        imported, skipped, fetched, normalized = await sync_platform_trades(session, platform)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except CapitalAPIError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
    return SyncResult(imported=imported, skipped=skipped, fetched=fetched, normalized=normalized)


@app.get("/api/trades", response_model=list[TradeRead])
def list_trades(session: Session = Depends(get_session)):
    rows = session.exec(select(Trade).order_by(Trade.closed_at.desc())).all()
    return rows


@app.get("/api/stats", response_model=list[PeriodStats])
def stats(period: str = "day", platform_id: int | None = None, session: Session = Depends(get_session)):
    period = period.lower()
    if period not in {"day", "month", "year"}:
        raise HTTPException(status_code=400, detail="period muss day | month | year sein")

    query = select(Trade)
    if platform_id is not None:
        query = query.where(Trade.platform_id == platform_id)
    trades = session.exec(query).all()

    grouped = defaultdict(list)
    for t in trades:
        dt = t.closed_at
        if period == "day":
            key = dt.strftime("%Y-%m-%d")
        elif period == "month":
            key = dt.strftime("%Y-%m")
        else:
            key = dt.strftime("%Y")
        grouped[key].append(t)

    result: list[PeriodStats] = []
    for key in sorted(grouped.keys(), reverse=True):
        chunk = grouped[key]
        pnl = sum(x.pnl for x in chunk)
        turnover = sum(abs(x.entry_price * x.quantity) for x in chunk) or 1.0
        pnl_pct = (pnl / turnover) * 100
        wins = [x for x in chunk if x.pnl > 0]
        losses = [x for x in chunk if x.pnl < 0]
        gross_profit = sum(x.pnl for x in wins)
        gross_loss_abs = abs(sum(x.pnl for x in losses))
        profit_factor = gross_profit / gross_loss_abs if gross_loss_abs > 0 else (999.0 if gross_profit > 0 else 0.0)

        result.append(
            PeriodStats(
                period=key,
                pnl_money=round(pnl, 2),
                pnl_percent=round(pnl_pct, 2),
                trades=len(chunk),
                winrate_percent=round((len(wins) / len(chunk)) * 100 if chunk else 0.0, 2),
                profit_factor=round(profit_factor, 2),
            )
        )
    return result
