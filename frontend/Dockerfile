# 1단계: 빌드
FROM node:18-alpine AS build

WORKDIR /app

# package.json과 package-lock.json 복사
COPY package*.json ./

# 의존성 설치
RUN npm ci

# 소스 코드 복사
COPY . .

# 빌드 실행
RUN npm run build

# 2단계: nginx로 정적 파일 서빙
FROM nginx:alpine

# nginx 설정 파일 복사 (필요시)
# COPY nginx.conf /etc/nginx/nginx.conf

# 빌드된 파일을 nginx 디렉토리로 복사
COPY --from=build /app/dist /usr/share/nginx/html

# 포트 노출
EXPOSE 80

# nginx 실행
CMD ["nginx", "-g", "daemon off;"] 