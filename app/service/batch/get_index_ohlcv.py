import logging
import os
from datetime import datetime
from app.db.database import SessionLocal
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from app.db.models.index_info import IndexInfo
import FinanceDataReader as fdr
import numpy as np
from app.db.models.index_ohlcv import IndexOhlcv
from dotenv import load_dotenv

logger = logging.getLogger('app.service.batch')

class IndexOhlcvService:
    def __init__(self):
        self.db = SessionLocal()

    def get_index_list(self):
        stmt = select(IndexInfo.name)
        return self.db.execute(stmt).scalars().all()

    def get_index_ohlcv(self, index_name, start_date, end_date):
        df = fdr.DataReader(index_name, start=start_date, end=end_date)
        df = df.rename(columns={
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume'
        })
        return df
    
    def upsert_index_ohlcv(self, index_name, df):
        df = df.replace({np.nan: None})
        df.reset_index(inplace=True)
        # 인덱스 이름이 'Date'이거나, 없을 때 모두 'ymd'로 컬럼명 변경
        if df.columns[0] != 'ymd':
            df.rename(columns={df.columns[0]: 'ymd'}, inplace=True)
        index_name_to_id = dict(self.db.query(IndexInfo.name, IndexInfo.id).all())
        df['name'] = index_name
        df['index_id'] = df['name'].map(index_name_to_id)
        model_columns = set(c.name for c in IndexOhlcv.__table__.columns)
        insert_df = df[[col for col in df.columns if col in model_columns]].copy()
        records = insert_df.to_dict(orient='records')
        if not records:
            logger.warning('적재할 데이터가 없습니다.')
            return
        stmt = insert(IndexOhlcv).values(records)
        stmt = stmt.on_conflict_do_update(
            index_elements=['index_id', 'ymd'],
            set_={col: getattr(stmt.excluded, col) for col in insert_df.columns if col not in ['index_id', 'ymd']}
        )
        self.db.execute(stmt)
        self.db.commit()
        logger.info(f"tb_index_ohlcv 테이블에 {len(records)}건 upsert 완료")

    def download_index_ohlcv(self, index_name, start_date, end_date):
        df = self.get_index_ohlcv(index_name, start_date, end_date)
        return df
    
    def download_and_upsert_all_index_ohlcv(self, start_date, end_date):
        for index_name in self.get_index_list():
            logger.debug(f"index_name: {index_name}")
            df = self.download_index_ohlcv(index_name, start_date, end_date)
            self.upsert_index_ohlcv(index_name, df)

def setup_logging():
    load_dotenv()
    ENV = os.getenv('ENV', 'development')
    # 로거 설정
    logger.setLevel(logging.WARNING)
    
    # 기존 핸들러 제거 (중복 방지)
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # 로그 디렉토리 생성
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # 로그 파일명 설정 (날짜 포함)
    today = datetime.now().strftime('%Y-%m-%d')
    log_filename = f'get_index_ohlcv_{today}.log'
    log_filepath = os.path.join(log_dir, log_filename)
    
    # 파일 핸들러 설정
    file_handler = logging.FileHandler(log_filepath, encoding='utf-8')
    file_handler.setLevel(logging.WARNING)
    
    # 포맷터 설정
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # 콘솔 핸들러는 production이 아닐 때만 추가
    if ENV != 'production':
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

def main():
    """메인 실행 함수"""
    setup_logging()
    index_ohlcv_service = IndexOhlcvService()
    index_ohlcv_service.download_and_upsert_all_index_ohlcv('2020-01-01', '2025-07-22')

if __name__ == '__main__':
    main()