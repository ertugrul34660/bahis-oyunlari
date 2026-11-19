@echo off
chcp 65001 > nul
title Ertuğrul YZ - Otonom Bahis ve Öğrenme Botu
echo ===============================================================
echo 🤖 ERTUĞRUL YZ - OTONOM BAHİS VE ÖZ-ÖĞRENME SENTINEL BOTU
echo 5. Kat: AR-GE, 3D Simülasyon, Oyun ve Spor Analiz Laboratuvarı
echo ===============================================================
echo.
cd /d "%~dp0"
python bot_kontrol.py simulate
echo.
echo [✓] İşlem tamamlandı. Durum panelini web tarayıcınızda açmak için bir tuşa basın...
start "" "..\ui\bot_dashboard.html"
exit
