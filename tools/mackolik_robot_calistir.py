# -*- coding: utf-8 -*-
"""
Ertuğrul YZ - Maçkolik Tarayan ve Öz-Öğrenen Robot Kontrol Aracı (CLI)
Kullanım:
    python mackolik_robot_calistir.py full_cycle
    python mackolik_robot_calistir.py scan
    python mackolik_robot_calistir.py status
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from core.mackolik_learning_robot import MackolikLearningRobot
from ui.mackolik_robot_dashboard_generator import generate_mackolik_dashboard_html

def run_full_learning_cycle():
    robot = MackolikLearningRobot()

    print("\n" + "=" * 70)
    print("🤖 ERTUĞRUL YZ - MAÇKOLİK İDDAA TARAYAN VE ÖĞRENEN ROBOT")
    print("=" * 70)

    # 1. ADIM: Canlı Maçkolik Bültenini Tara
    print("\n[ADIM 1] 📡 Maçkolik Canlı İddaa Bülteni taranıyor...")
    scan_res = robot.scan_and_bet_all(max_matches=8)
    if scan_res.get("durum") != "BAŞARILI":
        print(f"[!] Hata: {scan_res.get('mesaj')}")
        return

    print(f"[✓] Toplam {scan_res['taranan_toplam_mac']} Maçkolik maçı tarandı.")
    print(f"[✓] En yüksek değerli {scan_res['bahis_yapilan_mac']} maça sanal kasadan bahis oynandı:\n")

    for b in scan_res["bahisler"]:
        print(f"  • [{b['saat']}] {b['mac']:<35} ➔ Seçim: {b['secim']:<8} (Oran: {b['oran']:.2f} | Kasa: {b['yatirilan']:.2f} TL)")

    # 2. ADIM: Sonuçları Değerlendir ve Öğren
    print("\n[ADIM 2] 🧠 Karşılaşma Sonuçları İnceleniyor ve Öz-Öğrenme Döngüsü Başlatılıyor...")
    learn_reports = robot.resolve_and_learn_cycle()

    won_cnt = sum(1 for r in learn_reports if r["durum"] == "KAZANDI")
    lost_cnt = len(learn_reports) - won_cnt

    print(f"\n[✓] Sonuç Değerlendirmesi: {won_cnt} Kazandı / {lost_cnt} Kaybetti\n")

    for r in learn_reports:
        if r["durum"] == "KAZANDI":
            print(f"  ✓ [{r['mac']}] Tahmin: {r['tahmin']} | Gerçekleşen: {r['gerceklesen']} ({r['kazanc']:+,.2f} TL)")
            print(f"    Sonuç: İSABETLİ! Model parametreleri pekiştirildi.")
        else:
            print(f"  ❌ [{r['mac']}] Tahmin: {r['tahmin']} | Gerçekleşen: {r['gerceklesen']} ({r['kazanc']:+,.2f} TL)")
            print(f"    🔍 KÖK NEDEN OTOPSİSİ: {r['hata_koku']}")
            print(f"    📚 ALINAN DERS       : {r['alinan_ders']}")

    # 3. ADIM: Dashboard Güncelle
    html = generate_mackolik_dashboard_html()
    dash_path = project_root / "ui" / "mackolik_robot_dashboard.html"
    with open(dash_path, "w", encoding="utf-8") as f:
        f.write(html)

    bank = robot.bankroll.data
    weights = robot.learner.weights

    print("\n" + "=" * 70)
    print("📈 GÜNCEL KASA VE MODEL GELİŞİM DURUMU")
    print("-" * 70)
    print(f"💰 Sanal Kasa: {bank['guncel_kasa']:,.2f} TL (Net: {bank['net_kar_zarar']:+,.2f} TL | ROI: %{bank['roi_yuzde']})")
    print(f"🎯 Başarı Oranı: %{bank['basari_orani_yuzde']} ({bank['kazanan_bahis_sayisi']}W / {bank['kaybeden_bahis_sayisi']}L)")
    print("🧠 Güncellenen Karar Katsayıları:")
    for k, v in weights.get("agirliklar", {}).items():
        k_clean = k.replace("_", " ").title()
        print(f"   • {k_clean:<26}: %{v*100:.1f}")
    print("=" * 70)
    print(f"[✓] Maçkolik Robot Görsel Paneli Güncellendi: {dash_path}\n")

if __name__ == "__main__":
    run_full_learning_cycle()
