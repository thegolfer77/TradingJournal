from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class PlatformConfig(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    platform_type: str = Field(index=True)
    api_base_url: Optional[str] = None
    api_key: Optional[str] = None
    identifier: Optional[str] = None
    password: Optional[str] = None
    demo_mode: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Trade(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    platform_id: int = Field(index=True, foreign_key="platformconfig.id")
    external_trade_id: str = Field(index=True)
    symbol: str = Field(index=True)
    direction: str
    quantity: float
    entry_price: float
    exit_price: float
    pnl: float
    opened_at: datetime
    closed_at: datetime
    notes: Optional[str] = None
    imported_at: datetime = Field(default_factory=datetime.utcnow)
