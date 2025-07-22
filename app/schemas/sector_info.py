from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class SectorInfoBase(BaseModel):
    sector_code: str
    sector_name: str
    change_rate: float
    up_ticker_count: int
    neutral_ticker_count: int
    down_ticker_count: int
    detail_url: str
    ref: str

class SectorInfoResponse(SectorInfoBase):
    id: int
    crt_date: Optional[datetime]
    mod_date: Optional[datetime]

    class Config:
        orm_mode = True 