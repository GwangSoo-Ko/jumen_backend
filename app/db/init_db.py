import logging
import os
from dotenv import load_dotenv

# .env 환경변수 로드 및 ENV 확인
load_dotenv()
ENV = os.getenv('ENV', 'development')

# 로그 디렉토리 및 파일 설정
log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_filepath = os.path.join(log_dir, 'init_db.log')

logger = logging.getLogger('app.db')
logger.setLevel(logging.INFO)
for handler in logger.handlers[:]:
    logger.removeHandler(handler)
file_handler = logging.FileHandler(log_filepath, encoding='utf-8')
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# 개발환경에서는 콘솔 핸들러도 추가
if ENV != 'production':
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

from app.db.database import engine, Base
from app.db.models.kiwoom_api_info import KiwoomApiInfo
from app.db.models.stock_info import StockInfo
from app.db.models.stock_ohlcv import StockOhlcv
from app.db.models.stock_theme_relation import StockThemeRelation
from app.db.models.sector_info import SectorInfo
from app.db.models.stock_sector_relation import StockSectorRelation
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
    logger.info("DB 테이블 자동 생성 완료")
    
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
            logger.info("기본 전략 게시판 생성 완료")
        else:
            logger.info("기본 전략 게시판이 이미 존재합니다.")
            
        # 기본 지수 데이터 삽입
        existing_index = db.query(IndexInfo).first()
        if not existing_index:
            default_indices = [
                IndexInfo(name='KS11', description='KOSPI 지수', order_no=1),
                IndexInfo(name='KQ11', description='KOSDAQ 지수', order_no=2),
                IndexInfo(name='KS200', description='KOSPI200 지수', order_no=3),
                IndexInfo(name='DJI', description='다우존스 지수', order_no=4),
                IndexInfo(name='IXIC', description='나스닥 지수', order_no=5),
                IndexInfo(name='S&P500', description='S&P500 지수', order_no=6),
                IndexInfo(name='RUT', description='러셀 2000 지수', order_no=7),
                IndexInfo(name='VIX', description='VIX 지수', order_no=8),
                IndexInfo(name='USD/KRW', description='미국 달러/한국 원 환율', order_no=9),
                IndexInfo(name='BTC/KRW', description='비트코인/원화', order_no=10),
                IndexInfo(name='CL=F', description='WTI유 선물', order_no=11),
                IndexInfo(name='BZ=F', description='브렌트유 선물', order_no=12),
                IndexInfo(name='NG=F', description='천연가스 선물', order_no=13),
                IndexInfo(name='GC=F', description='금 선물', order_no=14),
                IndexInfo(name='SI=F', description='은 선물', order_no=15),
                IndexInfo(name='HG=F', description='구리 선물', order_no=16),
                IndexInfo(name='US5YT', description='5년 만기 미국채', order_no=17),
                IndexInfo(name='US10YT', description='10년 만기 미국채', order_no=18),
                IndexInfo(name='US30YT', description='30년 만기 미국채', order_no=19),
            ]
            db.add_all(default_indices)
            db.commit()
            logger.info("기본 지수 데이터 삽입 완료")
        else:
            logger.info("기본 지수 데이터가 이미 존재합니다.")
            
    except Exception as e:
        logger.error(f"데이터 생성 중 오류: {e}", exc_info=True)
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db()