from app.db.database import SessionLocal
from pykrx import stock
from datetime import datetime, timezone
import FinanceDataReader as fdr
import pandas as pd
from sqlalchemy.dialects.postgresql import insert
from app.db.models.stock_info import StockInfo
import logging
import warnings

warnings.filterwarnings('ignore')

logger = logging.getLogger('app.service.batch')

class StockInfoService:
    def __init__(self):
        self.db = SessionLocal()

    def upsert_stock_info(self, market_type: str):
        current_date = datetime.now().strftime("%Y%m%d")
        df = stock.get_market_fundamental(current_date, market_type)
        df.reset_index(inplace=True)
        fdr_df = fdr.StockListing(market_type)
        fdr_df = fdr_df[['Code', 'Name', 'Market', 'Marcap', 'Stocks']]
        df.rename(columns={'티커': 'ticker'}, inplace=True)
        fdr_df.rename(columns={'Code': 'ticker'}, inplace=True)
        fdr_df.rename(columns={'Name': 'name'}, inplace=True)
        fdr_df.rename(columns={'Market': 'market'}, inplace=True)
        fdr_df.rename(columns={'Marcap': 'market_cap'}, inplace=True)
        fdr_df.rename(columns={'Stocks': 'stock_count'}, inplace=True)

        df = df.merge(fdr_df, on='ticker', how='left')

        db = self.db

        stock_data_list = []
        try:
            if df.empty:
                logger.warning("No data found")
            else:
                for _, row in df.iterrows():
                    stock_data_list.append({
                        'ticker': row['ticker'],
                        'name': row['name'],
                        'market': row['market'],
                        'market_cap': row['market_cap'],
                        'stock_count': row['stock_count'],
                        'bps': row['BPS'],
                        'per': row['PER'],
                        'pbr': row['PBR'],
                        'eps': row['EPS'],
                        'div': row['DIV'],
                        'dps': row['DPS'],
                        'mod_date': datetime.now(timezone.utc)
                    })
                if stock_data_list:
                    stmt = insert(StockInfo).values(stock_data_list)
                    update_dict = {
                        'name': stmt.excluded.name,
                        'market': stmt.excluded.market,
                        'market_cap': stmt.excluded.market_cap,
                        'stock_count': stmt.excluded.stock_count,
                        'bps': stmt.excluded.bps,
                        'per': stmt.excluded.per,
                        'pbr': stmt.excluded.pbr,
                        'eps': stmt.excluded.eps,
                        'div': stmt.excluded.div,
                        'dps': stmt.excluded.dps,
                        'mod_date': stmt.excluded.mod_date
                    }
                    stmt = stmt.on_conflict_do_update(
                        index_elements=['ticker'],
                        set_=update_dict
                    )
                    db.execute(stmt)
                    db.commit()
                    logger.info(f"tb_stock_info 테이블에 {len(stock_data_list)}건 upsert 완료")
                else:
                    logger.warning("No data found")
        except Exception as e:
            logger.error(f"DB upsert 오류: {e}")
            db.rollback()
        finally:
            db.close()

def main():
    stock_info_service = StockInfoService()
    stock_info_service.upsert_stock_info('KOSPI')
    stock_info_service.upsert_stock_info('KOSDAQ')

if __name__ == '__main__':
    main()