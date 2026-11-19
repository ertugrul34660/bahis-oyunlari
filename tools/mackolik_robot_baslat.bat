@echo off
chcp 65001 > nul
title Ertuğrul YZ - Maçkolik Canlı Tarayıcı ve Öz-Öğrenen Robot
echo ======================================================================
echo 🤖 ERTUĞRUL YZ - MAÇKOLİK İDDAA TARAYAN VE ÖĞRENEN ROBOT
echo 5. Kat: Spor Analiz Laboratuvarı & Otonom Bahis Motoru
echo ======================================================================
echo.
cd /d "%~dp0"
python mackolik_robot_calistir.py
echo.
echo Paneli web tarayıcınızda açmak için bir tuşa basın...
start "" "..\ui\mackolik_robot_dashboard.html"
exit
