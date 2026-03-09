from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class PlatformCreate(BaseModel):
    name: str
    platform_type: str = Field(description="capital_com | generic_rest")
    api_base_url: Optional[str] = None
    api_key: Optional[str] = None
    identifier: Optional[str] = None
    password: Optional[str] = None
    demo_mode: bool = True


class PlatformRead(BaseModel):
    id: int
    name: str
    platform_type: str
    api_base_url: Optional[str]
    identifier: Optional[str]
    demo_mode: bool


class TradeRead(BaseModel):
    id: int
    platform_id: int
    external_trade_id: str
    symbol: str
    direction: str
    quantity: float
    entry_price: float
    exit_price: float
    pnl: float
    opened_at: datetime
    closed_at: datetime
    notes: Optional[str]


class SyncResult(BaseModel):
    imported: int
    skipped: int
