from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from app.db import get_session, init_db
from app.models import PlatformConfig, Trade
from app.schemas import PlatformCreate, PlatformRead, SyncResult, TradeRead
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
        imported, skipped = await sync_platform_trades(session, platform)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return SyncResult(imported=imported, skipped=skipped)


@app.get("/api/trades", response_model=list[TradeRead])
def list_trades(session: Session = Depends(get_session)):
    rows = session.exec(select(Trade).order_by(Trade.closed_at.desc())).all()
    return rows
