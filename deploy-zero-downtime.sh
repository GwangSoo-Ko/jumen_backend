#!/bin/bash

set -e

echo "==== 무중단 배포 시작 ===="

# 1. 최신 소스 가져오기
echo "1. 최신 소스 코드 가져오기"
git pull origin main

# 2. 환경변수 로드
echo "2. 환경변수 로드"
export $(cat env.production | xargs)

# 3. 새 이미지 빌드
echo "3. 새 이미지 빌드"
docker compose -f docker-compose.prod.yml build --no-cache

# 4. 새 컨테이너 시작 (기존과 다른 포트)
echo "4. 새 컨테이너 시작"
docker compose -f docker-compose.prod.yml up -d --scale backend=2

# 5. 새 컨테이너가 준비될 때까지 대기
echo "5. 새 컨테이너 준비 대기"
sleep 30

# 6. Health check
echo "6. Health check"
for i in {1..10}; do
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo "Health check 성공"
        break
    else
        echo "Health check 실패, 재시도 중... ($i/10)"
        sleep 10
    fi
done

# 7. 기존 컨테이너 제거
echo "7. 기존 컨테이너 제거"
docker compose -f docker-compose.prod.yml up -d --scale backend=1

# 8. 최종 상태 확인
echo "8. 최종 상태 확인"
docker compose -f docker-compose.prod.yml ps

echo "==== 무중단 배포 완료 ====" 