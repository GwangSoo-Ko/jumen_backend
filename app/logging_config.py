import logging
import os
from dotenv import load_dotenv

load_dotenv()
ENV = os.getenv('ENV', 'development')
LOG_DIR = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

LOG_CONFIG = {
    'app.api': os.path.join(LOG_DIR, 'api.log'),
    'app.service.batch': os.path.join(LOG_DIR, 'batch.log'),
    'app.service.kiwoom': os.path.join(LOG_DIR, 'kiwoom.log'),
    'app.db': os.path.join(LOG_DIR, 'db.log'),
    # 필요시 추가
}

LOG_FORMAT = '%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s - %(message)s'

# 이미 핸들러가 붙어있으면 중복 방지
_initialized = False

def setup_logging():
    global _initialized
    if _initialized:
        return
    for logger_name, log_path in LOG_CONFIG.items():
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.INFO)
        # 기존 핸들러 제거
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        file_handler = logging.FileHandler(log_path, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter(LOG_FORMAT)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        if ENV != 'production':
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
    _initialized = True 