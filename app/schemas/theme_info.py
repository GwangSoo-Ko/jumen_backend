from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ThemeInfoBase(BaseModel):
    theme_code: str
    theme_name: str
    change_rate: float
    avg_change_rate_3days: float
    up_ticker_count: int
    neutral_ticker_count: int
    down_ticker_count: int
    detail_url: str
    ref: str
    description: str

class ThemeInfoResponse(ThemeInfoBase):
    id: int
    crt_date: Optional[datetime]
    mod_date: Optional[datetime]

    class Config:
        orm_mode = True 