from fastapi import APIRouter, Depends, Query
from app.db.database import SessionLocal
from app.schemas.index_detail import IndexDetailResponse
from app.db.models.index_info import IndexInfo
from app.db.models.index_ohlcv import IndexOhlcv
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from collections import defaultdict

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/index/{index_id}", response_model=list[IndexDetailResponse])
def get_index_detail(index_id: int, db: Session = Depends(get_db)):
    last_30_days = datetime.now() - timedelta(days=30)
    results = (
        db.query(
            IndexOhlcv.index_id,
            IndexInfo.name,
            IndexOhlcv.ymd,
            IndexOhlcv.open,
            IndexOhlcv.high,
            IndexOhlcv.low,
            IndexOhlcv.close,
            IndexOhlcv.volume,
            IndexInfo.description
        )
        .join(IndexInfo, IndexInfo.id == IndexOhlcv.index_id)
        .filter(IndexOhlcv.index_id == index_id)
        .filter(IndexOhlcv.ymd >= last_30_days)
        .order_by(IndexOhlcv.ymd.asc())
        .all()
    )
    return [IndexDetailResponse(**dict(r._mapping)) for r in results]

@router.get("/index_all")
def get_index_detail_all(n_days: int = Query(30, ge=1, le=365), db: Session = Depends(get_db)):
    results = (
        db.query(
            IndexOhlcv.index_id,
            IndexInfo.name,
            IndexOhlcv.ymd,
            IndexOhlcv.open,
            IndexOhlcv.high,
            IndexOhlcv.low,
            IndexOhlcv.close,
            IndexOhlcv.volume,
            IndexInfo.description
        )
        .join(IndexInfo, IndexInfo.id == IndexOhlcv.index_id)
        .filter(IndexOhlcv.close.isnot(None))
        .order_by(IndexOhlcv.index_id.asc(), IndexOhlcv.ymd.asc())
        .all()
    )

    grouped = defaultdict(list)
    meta = {}

    for r in results:
        d = dict(r._mapping)
        idx = d['index_id']
        ohlcv = {
            'ymd': d['ymd'],
            'open': round(d['open'], 2),
            'high': round(d['high'], 2),
            'low': round(d['low'], 2),
            'close': round(d['close'], 2),
            'volume': d['volume'],
        }
        grouped[idx].append(ohlcv)
        if idx not in meta:
            meta[idx] = {
                'index_id': idx,
                'name': d['name'],
                'description': d['description'],
            }

    result = []
    for idx in grouped:
        # 마지막 n_days개만 슬라이싱
        ohlcv_list = grouped[idx][-n_days:]
        result.append({
            **meta[idx],
            'ohlcv': ohlcv_list
        })

    return result