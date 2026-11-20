#!/usr/bin/env bash
set -e

echo "============================================================"
echo "  INSTALASI OTOMATIS TIM AI AGENT (100% GRATIS DI VPS)"
echo "  n8n Self-Host + Mesin Render Video Motion 9:16 + HTTPS"
echo "============================================================"

if [ "$EUID" -ne 0 ]; then
  echo "[!] Jalankan script ini dengan sudo atau user root:"
  echo "    sudo bash install.sh"
  exit 1
fi

# 1. Pasang Docker & Docker Compose jika belum ada
if ! command -v docker &> /dev/null; then
  echo "[1/5] Memasang Docker di Ubuntu..."
  apt-get update -y
  apt-get install -y ca-certificates curl gnupg lsb-release
  curl -fsSL https://get.docker.com | sh
  systemctl enable --now docker
else
  echo "[1/5] Docker sudah terpasang."
fi

if ! docker compose version &> /dev/null; then
  echo "[+] Memasang plugin docker-compose..."
  apt-get update -y
  apt-get install -y docker-compose-v2 || apt-get install -y docker-compose-plugin
fi

# 2. Deteksi IP Publik VPS Biznet
PUBLIC_IP=$(curl -4 -s https://ifconfig.me || curl -4 -s https://api.ipify.org || echo "")
DASH_IP=$(echo "$PUBLIC_IP" | tr '.' '-')
DEFAULT_HOST="${DASH_IP}.sslip.io"

echo ""
echo "[2/5] Deteksi IP Publik VPS kamu: ${PUBLIC_IP}"
echo "      Jika kamu BELUM punya domain, tekan ENTER saja untuk memakai"
echo "      domain HTTPS otomatis gratis: ${DEFAULT_HOST}"
echo ""
read -r -p "Masukkan subdomain (atau tekan ENTER untuk pakai ${DEFAULT_HOST}): " INPUT_HOST

N8N_HOST="${INPUT_HOST:-$DEFAULT_HOST}"

cat > .env <<EOF
N8N_HOST=${N8N_HOST}
EOF

echo "[+] Menggunakan host: https://${N8N_HOST}"

# 3. Buka port firewall Ubuntu (UFW) jika aktif
if command -v ufw &> /dev/null && ufw status | grep -q "Status: active"; then
  echo "[3/5] Membuka port 80, 443, dan 5678 di UFW Firewall..."
  ufw allow 80/tcp
  ufw allow 443/tcp
  ufw allow 5678/tcp
else
  echo "[3/5] UFW tidak aktif, melewati konfigurasi UFW."
fi

# 4. Build & Jalankan Container
echo "[4/5] Membangun mesin Video Motion & menyalakan n8n (tunggu ~1-3 menit)..."
docker compose up -d --build

echo ""
echo "============================================================"
echo "  SELESAI! SISTEM AI AGENT & VIDEO MOTION SUDAH AKTIF"
echo "============================================================"
echo ""
echo "1. Buka Dashboard n8n di browser:"
echo "   https://${N8N_HOST}"
echo "   (Atau cadangan via IP jika port 80/443 Biznet belum dibuka: http://${PUBLIC_IP}:5678)"
echo ""
echo "2. PENTING untuk pengguna VPS Biznet Gio / NEO Cloud:"
echo "   Pastikan di Portal Biznet -> Security Group / Firewall VPS kamu,"
echo "   Inbound Rule sudah membuka port: TCP 80, TCP 443, dan TCP 5678."
echo ""
echo "3. URL Redirect OAuth2 untuk Google Cloud Console (Google Sheets):"
echo "   https://${N8N_HOST}/rest/oauth2-credential/callback"
echo ""
echo "4. URL Webhook untuk ditempel di Dashboard Fonnte (Device Nomor Bot):"
echo "   https://${N8N_HOST}/webhook/fonnte-tim-konten"
echo "============================================================"
