from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import theme_info
from app.api import index_info
from app.api import auth
from app.api import strategy_board
from app.api import free_board
from app.db.init_db import init_db

init_db()

app = FastAPI()

# CORS 미들웨어 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # 프론트엔드 개발 서버 주소
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(theme_info.router)
app.include_router(index_info.router)
app.include_router(auth.router)
app.include_router(strategy_board.router)
app.include_router(free_board.router)

@app.get("/")
def read_root():
    return {"message": "Stock Theme Backend API"}
