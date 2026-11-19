@echo off
chcp 65001 > nul
title Ertuğrul YZ - 7/24 Kesintisiz VPS Spor ve İddaa Motoru
echo ======================================================================
echo 🚀 ERTUĞRUL YZ - 7/24 KESİNTİSİZ VPS SPOR VE İDDAA ROBOTU
echo 5. Kat Spor Lab ⨉ 1. Kat 7/24 Bulut VPS Entegrasyonu
echo ======================================================================
echo.
cd /d "%~dp0"

echo [1] 7/24 VPS Nöbetçi Motorunu Başlat (Sessiz Arka Plan)
echo [2] Canlı VPS Nabız (Heartbeat) ve Kasa Durumunu İncele
echo [3] Maçkolik & Robot Gösterge Panelini Aç (Web)
echo [4] Bulut VPS (Docker / Linux) Dağıtım Bilgilerini Göster
echo.
choice /c 1234 /n /m "Seçiminiz (1, 2, 3 veya 4): "

if errorlevel 4 goto show_deploy
if errorlevel 3 goto open_ui
if errorlevel 2 goto check_status
if errorlevel 1 goto start_daemon

:start_daemon
echo.
echo [+] 7/24 VPS Spor Robotu arka planda sessizce başlatılıyor...
wscript.exe vps_arkaplanda_baslat.vbs
echo [✓] Robot arka planda kesintisiz nöbete başladı.
timeout /t 2 > nul
goto check_status

:check_status
echo.
echo ======================================================================
echo 💓 CANLI VPS SPOR ROBOTU NABIZ BİLGİSİ:
echo ======================================================================
type "..\data\vps_heartbeat.json"
echo.
echo Panel açılıyor...
start "" "..\ui\mackolik_robot_dashboard.html"
exit

:open_ui
start "" "..\ui\mackolik_robot_dashboard.html"
exit

:show_deploy
echo.
echo ======================================================================
echo ☁️ BULUT VPS DAĞITIM DOSYALARI HAZIR:
echo ======================================================================
echo • Dockerfile     : container\Dockerfile
echo • Compose        : container\docker-compose.yml
echo • Systemd Servis : container\systemd\ertugrul-spor-vps.service
echo • Deploy Scripti : vps\deploy_to_vps.sh
echo.
echo Linux VPS'e tek tıkla yüklemek için:
echo   bash vps/deploy_to_vps.sh <vps_ip_adresi>
echo.
pause
exit
