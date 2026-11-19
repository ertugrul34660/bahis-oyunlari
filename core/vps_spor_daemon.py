# -*- coding: utf-8 -*-
"""
Ertuğrul YZ - 7/24 Kesintisiz VPS Spor ve İddaa Nöbetçi Motoru (VPS Sports Daemon)
5. Kat: Spor Analiz Laboratuvarı & 2. Kat Finans Entegrasyonu

Görevler:
1. 7/24 durmaksızın Maçkolik bültenini izler.
2. Yeni çıkan maçları Quant Borsa mantığıyla filtreleyip otomatik sanal bahis açar.
3. Biten maçların skorlarını işler; kaybedilen maçlarda kök neden otopsisiyle modelini eğitir.
4. Hem yerel Windows arka planında hem de Linux Bulut VPS (Docker/systemd) üzerinde kesintisiz çalışır.
"""

import sys
import time
import json
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from core.mackolik_learning_robot import MackolikLearningRobot
from ui.mackolik_robot_dashboard_generator import generate_mackolik_dashboard_html

DATA_DIR = project_root / "data"
VPS_HEARTBEAT_FILE = DATA_DIR / "vps_heartbeat.json"

class VPSSportsDaemon:
    def __init__(self):
        self.robot = MackolikLearningRobot()
        self.start_time = datetime.now()
        self.cycle_count = 0
        self.scan_interval_seconds = 180  # Her 3 dakikada bir kontrol döngüsü

    def update_heartbeat(self, status_msg="7/24 NÖBETTE - BÜLTEN VE KASA AKTİF"):
        uptime = int((datetime.now() - self.start_time).total_seconds())
        bank = self.robot.bankroll.data
        hb = {
            "durum": "7/24 CANLI & NÖBETTE",
            "servis": "Ertuğrul YZ VPS Spor & Maçkolik Öğrenme Motoru",
            "son_nabiz": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "calisma_suresi_saniye": uptime,
            "toplam_dongu": self.cycle_count,
            "guncel_kasa": bank.get("guncel_kasa", 10000.0),
            "net_kar_zarar": bank.get("net_kar_zarar", 0.0),
            "basari_orani_yuzde": bank.get("basari_orani_yuzde", 0.0),
            "son_islem": status_msg
        }
        with open(VPS_HEARTBEAT_FILE, "w", encoding="utf-8") as f:
            json.dump(hb, f, ensure_ascii=False, indent=2)

    def run_one_cycle(self):
        self.cycle_count += 1
        now_str = datetime.now().strftime("%H:%M:%S")

        # 1. Bülteni Tara ve Bahisleri Kontrol Et
        scan_res = self.robot.scan_and_bet_all(max_matches=8)
        new_bets = scan_res.get("bahis_yapilan_mac", 0)

        # 2. Sonuçları Değerlendir ve Modeli Eğit
        learn_reports = self.robot.resolve_and_learn_cycle()
        won = sum(1 for r in learn_reports if r["durum"] == "KAZANDI")
        lost = len(learn_reports) - won

        # 3. Dashboard Güncelle
        html = generate_mackolik_dashboard_html()
        with open(project_root / "ui" / "mackolik_robot_dashboard.html", "w", encoding="utf-8") as f:
            f.write(html)

        msg = f"Döngü #{self.cycle_count}: {new_bets} maç analiz edildi | Sonuçlar: {won}W / {lost}L"
        self.update_heartbeat(msg)
        return msg

    def run_forever(self, interval_seconds: int = 180):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🚀 Ertuğrul YZ VPS Spor & İddaa 7/24 Nöbetçi Motoru Başlatıldı.")
        while True:
            try:
                msg = self.run_one_cycle()
                print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")
                time.sleep(interval_seconds)
            except KeyboardInterrupt:
                print("\n[!] VPS Spor motoru durduruldu.")
                break
            except Exception as e:
                print(f"[!] VPS Motor uyarı: {e}")
                self.update_heartbeat(f"Hata Kurtarma: {e}")
                time.sleep(interval_seconds)

if __name__ == "__main__":
    daemon = VPSSportsDaemon()
    if len(sys.argv) > 1 and sys.argv[1] == "--single":
        m = daemon.run_one_cycle()
        print(f"[✓] Tekli VPS döngüsü tamamlandı: {m}")
    else:
        # Arka plan servis modu (Varsayılan 3 dakika aralık)
        daemon.run_forever(interval_seconds=60)
