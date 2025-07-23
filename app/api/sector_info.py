import logging
logger = logging.getLogger('app.api')

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

@router.get('/sector/{sector_code}')
def get_sector(sector_code: str, db: Session = Depends(get_db)):
    sector = db.query(SectorInfo).filter(SectorInfo.sector_code == sector_code).first()
    if not sector:
        logger.warning(f'Sector not found: {sector_code}')
        raise HTTPException(status_code=404, detail='Sector not found')
    logger.info(f'Sector found: {sector_code}')
    return sector

@router.get('/sector/{sector_code}/stocks')
def get_sector_stocks(sector_code: str, db: Session = Depends(get_db)):
    sector = db.query(SectorInfo).filter(SectorInfo.sector_code == sector_code).first()
    if not sector:
        logger.warning(f'Sector not found: {sector_code}')
        raise HTTPException(status_code=404, detail='Sector not found')
    relations = db.query(StockSectorRelation).filter(StockSectorRelation.sector_id == sector.id).all()
    if not relations:
        logger.warning(f'No stock-sector relations for sector: {sector_code}')
        raise HTTPException(status_code=404, detail='No stock-sector relations found')
    logger.info(f'Stock-sector relations found for sector: {sector_code}, count={len(relations)}')
    return relations

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
    if not results:
        logger.warning(f'No results found for sector: {sector_id}')
        raise HTTPException(status_code=404, detail='No results found')
    logger.info(f'Sector detail found for sector: {sector_id}, count={len(results)}')
    return [SectorDetailResponse(**dict(r._mapping)) for r in results]