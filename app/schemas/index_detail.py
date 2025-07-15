from pydantic import BaseModel
from app.db.models.index_ohlcv import IndexOhlcv
from datetime import datetime

class IndexDetailBase(BaseModel):
    index_id: int
    ymd: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int

class IndexDetailResponse(BaseModel):
    index_id: int
    name: str
    ymd: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    description: str

    class Config:
        orm_mode = True 