from datetime import datetime
import time
from app.db.database import SessionLocal
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from app.db.models.stock_ohlcv import StockOhlcv
from app.db.models.stock_info import StockInfo
from pykrx import stock
import warnings
import talib
import numpy as np

warnings.filterwarnings('ignore')

class StockOhlcvService:
    def __init__(self):
        self.db = SessionLocal()

    def get_ticker_list(self, market_type: str):
        stmt = select(StockInfo.ticker).where(StockInfo.market == market_type)
        return self.db.execute(stmt).scalars().all()

    def upsert_stock_ohlcv(self, ticker, df):
        # 1. 모든 DataFrame을 하나로 합치기
        df = df.replace({np.nan: None})
        df['ticker'] = ticker
        df.reset_index(inplace=True)  # ymd를 컬럼으로 변환
        # 2. stock_id 매핑
        ticker_to_id = dict(self.db.query(StockInfo.ticker, StockInfo.id).all())
        df['stock_id'] = df['ticker'].map(ticker_to_id)
        # 3. DB 컬럼에 맞는 컬럼만 추출
        model_columns = set(c.name for c in StockOhlcv.__table__.columns)
        insert_df = df[[col for col in df.columns if col in model_columns]].copy()
        # 4. bulk upsert
        records = insert_df.to_dict(orient='records')
        if not records:
            print('적재할 데이터가 없습니다.')
            return
        stmt = insert(StockOhlcv).values(records)
        stmt = stmt.on_conflict_do_update(
            index_elements=['stock_id', 'ymd', 'ticker'],
            set_={col: getattr(stmt.excluded, col) for col in insert_df.columns if col not in ['stock_id', 'ymd', 'ticker']}
        )
        self.db.execute(stmt)
        self.db.commit()
        print(f"tb_stock_ohlcv 테이블에 {len(records)}건 upsert 완료")

    def chunk_list(self, lst, n):
        """리스트를 n개씩 잘라서 청크 단위로 반환"""
        for i in range(0, len(lst), n):
            yield lst[i:i+n]

    def download_krx_data(self, ticker_list, start_date, end_date, chunk_size=50, label=''):
        """
        pykrx를 이용해 주어진 티커 리스트의 OHLCV 데이터를
        start_date~end_date 기간 동안 chunk_size 단위로 받아옵니다.
        """
        result = {}
        sd = start_date.replace('-', '')
        ed = end_date.replace('-', '')
        for chunk in self.chunk_list(ticker_list, chunk_size):
            print(f"{label} 다운로드 중: {chunk[0]} ~ {chunk[-1]}")
            for tk in chunk:
                try:
                    df = stock.get_market_ohlcv_by_date(sd, ed, tk)
                    df = df.rename(columns={
                        '거래량': 'volume',
                        '시가': 'open',
                        '고가': 'high',
                        '저가': 'low',
                        '종가': 'close',
                        '등락률': 'change_rate',
                    })
                    df['trading_value'] = df['close'] * df['volume'] / 1e6  # 단위: 백만
                    df['open'] = df['open'].astype(np.float64)
                    df['high'] = df['high'].astype(np.float64)
                    df['low'] = df['low'].astype(np.float64)
                    df['close'] = df['close'].astype(np.float64)
                    df['volume'] = df['volume'].astype(np.float64)
                    df['trading_value'] = df['trading_value'].astype(np.float64)
                    df['change_rate'] = df['change_rate'].astype(np.float64)
                    df['change_rate'] = df['change_rate']/100
                    df.index.name = 'ymd'
                    result[tk] = df
                except Exception as e:
                    print(f"  ✗ {tk} 에러: {e}")
                time.sleep(1)
                try:
                    df = stock.get_market_trading_value_by_date(sd, ed, tk)
                    result[tk]['trading_value_institution'] = df['기관합계']
                    result[tk]['trading_value_other_corporation'] = df['기타법인']
                    result[tk]['trading_value_individual'] = df['개인']
                    result[tk]['trading_value_foreign'] = df['외국인합계']
                except Exception as e:
                    print(f"  ✗ {tk} 에러: {e}")
                time.sleep(1)
                try:
                    df = stock.get_market_trading_volume_by_date(sd, ed, tk)
                    result[tk]['volume_institution'] = df['기관합계']
                    result[tk]['volume_other_corporation'] = df['기타법인']
                    result[tk]['volume_individual'] = df['개인']
                    result[tk]['volume_foreign'] = df['외국인합계']
                except Exception as e:
                    print(f"  ✗ {tk} 에러: {e}")
                time.sleep(1)
                self.add_indicators(result[tk])

        return result
    
    def add_indicators(self,df):
        # 1. EMA (5, 20, 60, 120, 240, 480)
        for period in [5, 20, 60, 120, 240, 480]:
            df[f'sma_{period}'] = talib.SMA(df['close'].values, timeperiod=period)
            df[f'ema_{period}'] = talib.EMA(df['close'].values, timeperiod=period)

        # 2. RSI (14일)
        df['rsi'] = talib.RSI(df['close'].values, timeperiod=14)

        # 3. MACD (fast=12, slow=26, signal=9)
        macd, macdsignal, macdhist = talib.MACD(df['close'].values,
                                                fastperiod=12, slowperiod=26, signalperiod=9)
        df['macd'] = macd
        df['macd_signal'] = macdsignal
        df['macd_hist'] = macdhist

        # 4. Bollinger Bands (20일, 2표준편차)
        upper, middle, lower = talib.BBANDS(df['close'].values,
                                            timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
        df['bb_upper'] = upper
        df['bb_middle'] = middle
        df['bb_lower'] = lower

        # 5. Stochastic Oscillator (fastk=14, slowk=3, slowd=3)
        slowk, slowd = talib.STOCH(df['high'].values, df['low'].values, df['close'].values,
                                fastk_period=14, slowk_period=3, slowk_matype=0,
                                slowd_period=3, slowd_matype=0)
        df['stoch_k'] = slowk
        df['stoch_d'] = slowd

        # 6. OBV (On Balance Volume)
        df['obv'] = talib.OBV(df['close'].values, df['volume'].values)

        # 7. MFI (14일)
        df['mfi'] = talib.MFI(df['high'].values, df['low'].values, df['close'].values,
                            df['volume'].values, timeperiod=14)

        # 8. Fibonacci Retracement (전체 구간 기준)
        max_price = df['close'].max()
        min_price = df['close'].min()
        df['fib_0']    = max_price
        df['fib_23_6'] = max_price - 0.236 * (max_price - min_price)
        df['fib_38_2'] = max_price - 0.382 * (max_price - min_price)
        df['fib_50']   = max_price - 0.5   * (max_price - min_price)
        df['fib_61_8'] = max_price - 0.618 * (max_price - min_price)
        df['fib_100']  = min_price

        # 9. Ichimoku Cloud
        period9 = 9
        period26 = 26
        period52 = 52
        displacement = 26
        high9 = df['high'].rolling(window=period9).max()
        low9  = df['low'].rolling(window=period9).min()
        df['tenkan_sen'] = (high9 + low9) / 2
        high26 = df['high'].rolling(window=period26).max()
        low26  = df['low'].rolling(window=period26).min()
        df['kijun_sen'] = (high26 + low26) / 2
        df['senkou_span_a'] = ((df['tenkan_sen'] + df['kijun_sen']) / 2).shift(displacement)
        high52 = df['high'].rolling(window=period52).max()
        low52  = df['low'].rolling(window=period52).min()
        df['senkou_span_b'] = ((high52 + low52) / 2).shift(displacement)
        df['chikou_span'] = df['close'].shift(-displacement)

        # 10. CCI (14일)
        df['cci'] = talib.CCI(df['high'].values, df['low'].values, df['close'].values, timeperiod=14)

        # 11. VWAP (누적 방식)
        df['vwap'] = (df['close'] * df['volume']).cumsum() / df['volume'].cumsum()

        # 12. ATR (14일)
        df['atr'] = talib.ATR(df['high'].values, df['low'].values, df['close'].values, timeperiod=14)

        # 13. ADX (14일)
        df['adx'] = talib.ADX(df['high'].values, df['low'].values, df['close'].values, timeperiod=14)

        # 14. Pivot Point (Pivot, R1, S1, R2, S2)
        df['pivot'] = (df['high'] + df['low'] + df['close']) / 3
        df['r1'] = (2 * df['pivot']) - df['low']
        df['s1'] = (2 * df['pivot']) - df['high']
        df['r2'] = df['pivot'] + (df['high'] - df['low'])
        df['s2'] = df['pivot'] - (df['high'] - df['low'])

        # 15. Volume Moving Average (5일)
        df['avg_volume_5'] = df['volume'].rolling(window=5).mean()
        df['avg_trading_value_5'] = df['trading_value'].rolling(window=5).mean()

        return df


if __name__ == '__main__':
    start_time = time.time()
    stock_ohlcv_service = StockOhlcvService()
    market_type = 'KOSPI'
    ticker_list = stock_ohlcv_service.get_ticker_list(market_type)
    for ticker_sub in ticker_list:
        ticker_list = [ticker_sub]
        start_date = '2024-01-01'
        end_date = datetime.now().strftime('%Y-%m-%d')
        df = stock_ohlcv_service.download_krx_data(ticker_list, start_date, end_date, chunk_size=50, label=market_type)
        print(f"ticker: {ticker_sub} 데이터 다운로드 소요시간: {time.time() - start_time}초")
        start_time = time.time()
        for ticker, df in df.items():
            stock_ohlcv_service.upsert_stock_ohlcv(ticker, df)
        print(f"ticker: {ticker_sub} DB 업데이트 소요시간: {time.time() - start_time}초")