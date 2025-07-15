from app.db.database import SessionLocal
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from app.db.models.index_info import IndexInfo
import FinanceDataReader as fdr
import numpy as np
from app.db.models.index_ohlcv import IndexOhlcv

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
            print('적재할 데이터가 없습니다.')
            return
        stmt = insert(IndexOhlcv).values(records)
        stmt = stmt.on_conflict_do_update(
            index_elements=['index_id', 'ymd'],
            set_={col: getattr(stmt.excluded, col) for col in insert_df.columns if col not in ['index_id', 'ymd']}
        )
        self.db.execute(stmt)
        self.db.commit()
        print(f"tb_index_ohlcv 테이블에 {len(records)}건 upsert 완료")

    def download_index_ohlcv(self, index_name, start_date, end_date):
        df = self.get_index_ohlcv(index_name, start_date, end_date)
        return df
    
    def download_and_upsert_all_index_ohlcv(self, start_date, end_date):
        for index_name in self.get_index_list():
            print(f"index_name: {index_name}")
            df = self.download_index_ohlcv(index_name, start_date, end_date)
            self.upsert_index_ohlcv(index_name, df)


if __name__ == '__main__':
    index_ohlcv_service = IndexOhlcvService()
    index_ohlcv_service.download_and_upsert_all_index_ohlcv('2020-01-01', '2025-07-14')