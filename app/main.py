from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import theme_info

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

@app.get("/")
def read_root():
    return {"message": "Stock Theme Backend API"}
