from app.db.database import engine, Base

from app.db.models.kiwoom_api_info import KiwoomApiInfo
from app.db.models.stock_info import StockInfo
from app.db.models.stock_ohlcv import StockOhlcv
from app.db.models.stock_theme_relation import StockThemeRelation
from app.db.models.theme_info import ThemeInfo
from app.db.models.index_info import IndexInfo
from app.db.models.index_ohlcv import IndexOhlcv
from app.db.models.user import User
from app.db.models.account import Account
from app.db.models.refresh_token import RefreshToken
from app.db.models.strategy_board import StrategyBoard

# 필요한 모든 Base import

def init_db():
    # 모든 Base에 대해 create_all 호출
    Base.metadata.create_all(engine)
    print("DB 테이블 자동 생성 완료")
    
    # 기본 전략 게시판 생성
    from app.db.database import SessionLocal
    db = SessionLocal()
    try:
        # 기본 전략 게시판이 있는지 확인
        existing_board = db.query(StrategyBoard).filter(StrategyBoard.id == 1).first()
        if not existing_board:
            default_board = StrategyBoard(
                id=1,
                name="전략 게시판",
                description="투자 전략을 공유하는 게시판입니다.",
                is_active=True,
                sort_order=1,
                max_risk_level=5,
                allowed_strategy_types=['buy', 'sell', 'hold', 'analysis'],
                require_stock_reference=False,
                require_theme_reference=False,
                allow_anonymous=False,
                max_tags_count=10,
                require_target_price=False,
                require_risk_assessment=True
            )
            db.add(default_board)
            db.commit()
            print("기본 전략 게시판 생성 완료")
        else:
            print("기본 전략 게시판이 이미 존재합니다.")
    except Exception as e:
        print(f"전략 게시판 생성 중 오류: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db()