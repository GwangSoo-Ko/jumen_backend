from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime

class StockInfoBase(BaseModel):
    ticker: str
    name: str
    market: Optional[str]
    sector: Optional[str]
    listed_date: Optional[date]
    size: Optional[str]
    company_class: Optional[str]
    listed_count: Optional[int]
    warning_status: Optional[str]

class StockInfoResponse(StockInfoBase):
    id: int
    crt_date: Optional[datetime]
    mod_date: Optional[datetime]

    class Config:
        orm_mode = True 