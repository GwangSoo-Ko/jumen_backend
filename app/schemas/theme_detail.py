from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class ThemeDetailBase(BaseModel):
    stock_id: int
    theme_id: int
    current_price: Optional[float]
    diff_price: Optional[float]
    change_rate: Optional[float]
    volume: Optional[int]
    trading_value: Optional[float]
    volume_yesterday: Optional[int]
    description: Optional[str]

class ThemeDetailResponse(BaseModel):
    stock_id: int
    ticker: str
    name: str
    theme_id: int
    theme_name: str
    current_price: Optional[float]
    diff_price: Optional[float]
    change_rate: Optional[float]
    volume: Optional[int]
    trading_value: Optional[float]
    volume_yesterday: Optional[int]
    description: Optional[str]
    crt_date: Optional[datetime]
    mod_date: Optional[datetime]

    class Config:
        orm_mode = True 
    