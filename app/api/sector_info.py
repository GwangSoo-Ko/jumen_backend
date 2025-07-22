from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import SessionLocal
from app.db.models.sector_info import SectorInfo
from app.db.models.stock_sector_relation import StockSectorRelation
from app.db.models.stock_info import StockInfo
from app.schemas.sector_info import SectorInfoResponse
from app.schemas.sector_detail import SectorDetailResponse

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/sectors", response_model=List[SectorInfoResponse])
def read_sectors(db: Session = Depends(get_db)):
    sectors = db.query(SectorInfo).order_by(SectorInfo.change_rate.desc()).all()
    if not sectors:
        raise HTTPException(status_code=404, detail="Sectors not found")
    return sectors

@router.get("/sectors/{sector_id}", response_model=list[SectorDetailResponse])
def read_sector_detail(sector_id: int, db: Session = Depends(get_db)):
    results = (
        db.query(
            StockSectorRelation.stock_id,
            StockInfo.ticker,
            StockInfo.name,
            StockSectorRelation.sector_id,
            SectorInfo.sector_name,
            StockSectorRelation.current_price,
            StockSectorRelation.diff_price,
            StockSectorRelation.change_rate,
            StockSectorRelation.volume,
            StockSectorRelation.trading_value,
            StockSectorRelation.volume_yesterday,
            StockSectorRelation.crt_date,
            StockSectorRelation.mod_date,
        )
        .join(StockInfo, StockSectorRelation.stock_id == StockInfo.id)
        .join(SectorInfo, StockSectorRelation.sector_id == SectorInfo.id)
        .filter(StockSectorRelation.sector_id == sector_id)
        .all()
    )
    return [SectorDetailResponse(**dict(r._mapping)) for r in results]