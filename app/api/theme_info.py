import logging
logger = logging.getLogger('app.api')

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import SessionLocal
from app.db.models.theme_info import ThemeInfo
from app.db.models.stock_theme_relation import StockThemeRelation
from app.db.models.stock_info import StockInfo
from app.schemas.theme_info import ThemeInfoResponse
from app.schemas.theme_detail import ThemeDetailResponse

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/themes", response_model=List[ThemeInfoResponse])
def read_themes(db: Session = Depends(get_db)):
    themes = db.query(ThemeInfo).order_by(ThemeInfo.change_rate.desc()).all()
    if not themes:
        raise HTTPException(status_code=404, detail="Themes not found")
    return themes

@router.get('/theme/{theme_code}')
def get_theme(theme_code: str, db: Session = Depends(get_db)):
    theme = db.query(ThemeInfo).filter(ThemeInfo.theme_code == theme_code).first()
    if not theme:
        logger.warning(f'Theme not found: {theme_code}')
        raise HTTPException(status_code=404, detail='Theme not found')
    logger.info(f'Theme found: {theme_code}')
    return theme

@router.get('/theme/{theme_code}/stocks')
def get_theme_stocks(theme_code: str, db: Session = Depends(get_db)):
    theme = db.query(ThemeInfo).filter(ThemeInfo.theme_code == theme_code).first()
    if not theme:
        logger.warning(f'Theme not found: {theme_code}')
        raise HTTPException(status_code=404, detail='Theme not found')
    relations = db.query(StockThemeRelation).filter(StockThemeRelation.theme_id == theme.id).all()
    if not relations:
        logger.warning(f'No stock-theme relations for theme: {theme_code}')
        raise HTTPException(status_code=404, detail='No stock-theme relations found')
    logger.info(f'Stock-theme relations found for theme: {theme_code}, count={len(relations)}')
    return relations

@router.get("/themes/{theme_id}", response_model=list[ThemeDetailResponse])
def read_theme_detail(theme_id: int, db: Session = Depends(get_db)):
    results = (
        db.query(
            StockThemeRelation.stock_id,
            StockInfo.ticker,
            StockInfo.name,
            StockThemeRelation.theme_id,
            ThemeInfo.theme_name,
            StockThemeRelation.current_price,
            StockThemeRelation.diff_price,
            StockThemeRelation.change_rate,
            StockThemeRelation.volume,
            StockThemeRelation.trading_value,
            StockThemeRelation.volume_yesterday,
            StockThemeRelation.description,
            StockThemeRelation.crt_date,
            StockThemeRelation.mod_date,
        )
        .join(StockInfo, StockThemeRelation.stock_id == StockInfo.id)
        .join(ThemeInfo, StockThemeRelation.theme_id == ThemeInfo.id)
        .filter(StockThemeRelation.theme_id == theme_id)
        .all()
    )
    if not results:
        logger.warning(f'No results found for theme: {theme_id}')
        raise HTTPException(status_code=404, detail='No results found')
    logger.info(f'Theme detail found for theme: {theme_id}, count={len(results)}')
    return [ThemeDetailResponse(**dict(r._mapping)) for r in results]