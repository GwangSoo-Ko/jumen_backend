#!/bin/bash

set -e  # 에러 발생 시 즉시 종료

echo "==== [1] 최신 소스 코드 가져오기 ===="
git pull origin main

echo "==== [2] Docker 이미지 빌드 ===="
docker compose build --no-cache

echo "==== [3] 컨테이너 재시작 ===="
docker compose up -d

echo "==== [4] 컨테이너 상태 확인 ===="
docker compose ps

echo "==== [5] 불필요한 이미지/컨테이너 정리 ===="
docker system prune -f

echo "==== [배포 완료] ===="
echo "백엔드 API: http://localhost:8000"
echo "프론트엔드: http://localhost:80"
echo "데이터베이스: localhost:5432" 