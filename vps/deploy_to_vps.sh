#!/usr/bin/env bash
# ==============================================================================
# Ertuğrul YZ - 7/24 Kesintisiz Spor & İddaa Robotunu Bulut VPS'e Dağıtım Scripti
# Kullanım: ./deploy_to_vps.sh <vps_ip> [user]
# ==============================================================================

set -e

VPS_IP="${1:-}"
VPS_USER="${2:-root}"
REMOTE_DIR="/opt/ertugrul-spor-vps"

if [ -z "$VPS_IP" ]; then
    echo "❌ HATA: Lütfen hedef VPS IP adresini belirtin!"
    echo "Kullanım: ./deploy_to_vps.sh <vps_ip> [user]"
    exit 1
fi

echo "🚀 [1/4] Hedef VPS'e bağlanılıyor: $VPS_USER@$VPS_IP..."
ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_IP" "mkdir -p $REMOTE_DIR"

echo "📦 [2/4] Proje dosyaları VPS'e senkronize ediliyor..."
rsync -avz --exclude '__pycache__' --exclude '.git' \
    ../core ../ui ../data ../container "$VPS_USER@$VPS_IP:$REMOTE_DIR/"

echo "⚙️ [3/4] VPS üzerinde Docker & Systemd servisi hazırlanıyor..."
ssh "$VPS_USER@$VPS_IP" << 'EOF'
cd /opt/ertugrul-spor-vps
if command -v docker-compose &> /dev/null; then
    echo "🐳 Docker Compose ile 7/24 Container ayağa kaldırılıyor..."
    cd container && docker-compose up -d --build
else
    echo "🐧 Systemd servisi ile 7/24 arka planda başlatılıyor..."
    cp container/systemd/ertugrul-spor-vps.service /etc/systemd/system/
    systemctl daemon-reload
    systemctl enable ertugrul-spor-vps
    systemctl restart ertugrul-spor-vps
fi
EOF

echo "✅ [4/4] Ertuğrul YZ Spor & İddaa Robotu VPS üzerinde 7/24 Nöbete Başladı!"
echo "💓 Canlı durum için: ssh $VPS_USER@$VPS_IP 'systemctl status ertugrul-spor-vps'"
