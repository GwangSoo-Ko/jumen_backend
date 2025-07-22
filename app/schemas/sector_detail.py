from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class SectorDetailBase(BaseModel):
    stock_id: int
    sector_id: int
    current_price: Optional[float]
    diff_price: Optional[float]
    change_rate: Optional[float]
    volume: Optional[int]
    trading_value: Optional[float]
    volume_yesterday: Optional[int]

class SectorDetailResponse(BaseModel):
    stock_id: int
    ticker: str
    name: str
    sector_id: int
    sector_name: str
    current_price: Optional[float]
    diff_price: Optional[float]
    change_rate: Optional[float]
    volume: Optional[int]
    trading_value: Optional[float]
    volume_yesterday: Optional[int]
    crt_date: Optional[datetime]
    mod_date: Optional[datetime]

    class Config:
        orm_mode = True 