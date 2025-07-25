from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class StockInfoBase(BaseModel):
    ticker: str
    name: str
    market: Optional[str]
    stock_count: Optional[int]
    market_cap: Optional[int]
    bps: Optional[int]
    per: Optional[float]
    pbr: Optional[float]
    eps: Optional[int]
    div: Optional[float]
    dps: Optional[int]

class StockInfoResponse(StockInfoBase):
    id: int
    crt_date: Optional[datetime]
    mod_date: Optional[datetime]

    class Config:
        orm_mode = True 