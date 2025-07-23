#!/bin/bash

# Let's Encrypt SSL 인증서 자동 발급 스크립트

DOMAIN="yourdomain.com"
EMAIL="your-email@example.com"

echo "==== SSL 인증서 발급 시작 ===="

# certbot 설치 (Ubuntu/Debian 기준)
sudo apt-get update
sudo apt-get install -y certbot

# SSL 인증서 발급
sudo certbot certonly --standalone \
    --email $EMAIL \
    --agree-tos \
    --no-eff-email \
    -d $DOMAIN \
    -d www.$DOMAIN

# 인증서를 nginx에서 사용할 수 있도록 복사
sudo mkdir -p ssl
sudo cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem ssl/
sudo cp /etc/letsencrypt/live/$DOMAIN/privkey.pem ssl/

# 권한 설정
sudo chmod 644 ssl/fullchain.pem
sudo chmod 600 ssl/privkey.pem

echo "==== SSL 인증서 발급 완료 ===="
echo "인증서 위치: ssl/fullchain.pem, ssl/privkey.pem"

# 자동 갱신 설정 (cron에 추가)
echo "0 12 * * * /usr/bin/certbot renew --quiet --deploy-hook 'systemctl reload nginx'" | sudo crontab - 