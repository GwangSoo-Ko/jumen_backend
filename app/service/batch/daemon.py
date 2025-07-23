import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio
from datetime import datetime

logger = logging.getLogger('app.service.batch')

scheduler = None  # 전역 스케줄러 인스턴스

# 각 배치 작업을 함수로 래핑
def run_crawl_naver_theme_info():
    try:
        from app.service.batch import crawl_naver_theme_info
        asyncio.run(crawl_naver_theme_info.main())
        logger.info('crawl_naver_theme_info 실행 완료')
    except Exception as e:
        logger.exception(f'crawl_naver_theme_info 실행 오류: {e}')

def run_crawl_naver_sector_info():
    try:
        from app.service.batch import crawl_naver_sector_info
        asyncio.run(crawl_naver_sector_info.main())
        logger.info('crawl_naver_sector_info 실행 완료')
    except Exception as e:
        logger.exception(f'crawl_naver_sector_info 실행 오류: {e}')

def run_get_index_ohlcv():
    try:
        from app.service.batch import get_index_ohlcv
        # main() 함수를 호출하여 로깅 설정이 적용되도록 함
        get_index_ohlcv.main()
        logger.info('get_index_ohlcv 실행 완료')
    except Exception as e:
        logger.exception(f'get_index_ohlcv 실행 오류: {e}')

def run_get_stock_info():
    try:
        from app.service.batch import get_stock_info
        # main() 함수를 호출하여 로깅 설정이 적용되도록 함
        get_stock_info.main()
        logger.info('get_stock_info 실행 완료')
    except Exception as e:
        logger.exception(f'get_stock_info 실행 오류: {e}')

async def start_scheduler():
    global scheduler
    if scheduler is None:
        scheduler = AsyncIOScheduler()
        scheduler.add_job(run_crawl_naver_theme_info, 'cron', minute='*/10', hour='9-16', id='theme_info')
        scheduler.add_job(run_crawl_naver_sector_info, 'cron', minute='*/10', hour='9-16', id='sector_info')
        scheduler.add_job(run_get_index_ohlcv, 'cron', hour=17, minute=0, id='index_ohlcv')
        scheduler.add_job(run_get_stock_info, 'cron', hour=17, minute=0, id='stock_info')
        scheduler.start()
        logger.info('배치 데몬 서비스 시작')
    return scheduler

async def shutdown_scheduler():
    global scheduler
    if scheduler is not None:
        scheduler.shutdown(wait=True)
        logger.info('배치 데몬 서비스 종료')
        scheduler = None

if __name__ == '__main__':
    import asyncio
    async def main():
        await start_scheduler()
        try:
            while True:
                await asyncio.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            await shutdown_scheduler()
    asyncio.run(main()) 