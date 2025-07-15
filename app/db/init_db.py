from app.db.database import engine, Base

from app.db.models.kiwoom_api_info import KiwoomApiInfo
from app.db.models.stock_info import StockInfo
from app.db.models.stock_ohlcv import StockOhlcv
from app.db.models.stock_theme_relation import StockThemeRelation
from app.db.models.theme_info import ThemeInfo
from app.db.models.index_info import IndexInfo
from app.db.models.index_ohlcv import IndexOhlcv

# 필요한 모든 Base import

def init_db():
    # 모든 Base에 대해 create_all 호출
    Base.metadata.create_all(engine)
    print("DB 테이블 자동 생성 완료")

if __name__ == "__main__":
    init_db()