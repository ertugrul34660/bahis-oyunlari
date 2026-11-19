# -*- coding: utf-8 -*-
"""
Ertuğrul YZ - Otonom Bahis ve Öğrenme Botu Kontrol Paneli (CLI)
Kullanım:
    python bot_kontrol.py status
    python bot_kontrol.py simulate
    python bot_kontrol.py bet "Badajoz" "Tenerife" 1.47 "MS 2"
"""

import sys
import json
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from core.bot_daemon import AutonomousBettingBot

def show_status():
    bot = AutonomousBettingBot()
    bank = bot.bankroll.data
    weights = bot.learner.weights

    print("\n" + "=" * 65)
    print("🤖 ERTUĞRUL YZ - OTONOM BAHİS VE ÖZ-ÖĞRENME BOTU DURUM RAPORU")
    print("=" * 65)
    print(f"💰 Sanal Kasa Bakiyesi   : {bank['guncel_kasa']:,.2f} TL (Başlangıç: {bank['baslangic_kasa']:,.2f} TL)")
    print(f"📈 Net Kâr / Zarar       : {bank['net_kar_zarar']:+,.2f} TL (ROI: %{bank['roi_yuzde']})")
    print(f"🎯 Başarı Oranı          : %{bank['basari_orani_yuzde']} ({bank['kazanan_bahis_sayisi']} Kazandı / {bank['kaybeden_bahis_sayisi']} Kaybetti)")
    print(f"🔄 Toplam Öğrenme Adımı  : {weights.get('toplam_ogrenme_adimi', 0)}")
    print("-" * 65)
    print("🧠 Güncel Dinamik Model Ağırlıkları (Öğrenilen Katsayılar):")
    for k, v in weights.get("agirliklar", {}).items():
        k_clean = k.replace("_", " ").title()
        print(f"  • {k_clean:<28}: %{v*100:.1f}")

    print("-" * 65)
    print("💡 Son Öğrenilen Dersler (Kök Neden Otopsisi):")
    log_file = project_root / "data" / "ogrenme_gunlugu.json"
    if log_file.exists():
        with open(log_file, "r", encoding="utf-8") as f:
            logs = json.load(f)
            for log in logs[-3:]:
                if log.get("sonuc") == "KAYBETTİ":
                    print(f"  ❌ [{log.get('mac')}]")
                    print(f"     🔍 Hata Kökü   : {log.get('hata_koku')}")
                    print(f"     📚 Alınan Ders : {log.get('alinan_ders')}")
                elif log.get("sonuc") == "KAZANDI":
                    print(f"  ✓ [{log.get('mac')}] Başarılı tahmin, parametreler pekiştirildi.")
    print("=" * 65 + "\n")

def run_simulation():
    bot = AutonomousBettingBot()
    print("\n[+] Örnek maçlar üzerinden Otonom Bahis ve Öğrenme Simülasyonu başlatılıyor...\n")

    test_matches = [
        # Maç 1: Badajoz vs Tenerife (Deplasman yol yorgunluğu ve rotasyon -> Maç 0-0 bitti ve 2.5 Alt kazandı)
        {
            "ev_sahibi": "CD Badajoz",
            "deplasman": "CD Tenerife",
            "ev_ozellikler": {"kadro": 0.35, "form": 0.65, "dinlenme": 0.9},
            "dep_ozellikler": {"kadro": 0.75, "form": 0.55, "dinlenme": 0.5, "seyahat": 0.85},
            "oranlar": {"ms_1": 4.44, "ms_x": 3.36, "ms_2": 1.47, "alt_25": 1.55},
            "gercek_sonuc": "2.5 Alt"
        },
        # Maç 2: Örnek Favori Deplasman Kaybı (Model MS 2 dedi ama Tenerife berabere kaldı -> Hata otopsisi tetiklenir)
        {
            "ev_sahibi": "CD Don Benito",
            "deplasman": "Real Zaragoza",
            "ev_ozellikler": {"kadro": 0.30, "form": 0.70, "dinlenme": 0.85},
            "dep_ozellikler": {"kadro": 0.80, "form": 0.60, "dinlenme": 0.4, "seyahat": 0.75},
            "oranlar": {"ms_1": 4.80, "ms_x": 3.40, "ms_2": 1.45, "alt_25": 1.60},
            "gercek_sonuc": "MS X"
        },
        # Maç 3: Ev Sahibi Banko (Real Madrid vs Alaves)
        {
            "ev_sahibi": "Real Madrid",
            "deplasman": "Alaves",
            "ev_ozellikler": {"kadro": 0.95, "form": 0.85, "dinlenme": 0.8},
            "dep_ozellikler": {"kadro": 0.40, "form": 0.35, "dinlenme": 0.5, "seyahat": 0.5},
            "oranlar": {"ms_1": 1.25, "ms_x": 5.50, "ms_2": 9.00, "alt_25": 2.40},
            "gercek_sonuc": "MS 1"
        }
    ]

    for idx, m in enumerate(test_matches, 1):
        print(f"--- [Maç {idx}: {m['ev_sahibi']} vs {m['deplasman']}] ---")
        res = bot.process_match(m, actual_result=m.get("gercek_sonuc"))
        print(f"• Seçilen Bahis     : {res['tahmin']} (Oran: {res['oran']:.2f}, Güven: %{res['guven']})")
        print(f"• Yatırılan Tutar   : {res['yatirilan_tutar']:.2f} TL")
        print(f"• Gerçekleşen Sonuç : {m.get('gercek_sonuc')}")
        print(f"• Karar & Durum     : {res['sonuc']} ({res.get('kazanc_kayip', 0):+,.2f} TL)")
        if res['sonuc'] == "KAYBETTİ":
            print(f"  🔍 KÖK NEDEN OTOPSİSİ : {res.get('hata_koku')}")
            print(f"  📚 ALINAN DERS        : {res.get('alinan_ders')}")
        print()

    print("[✓] Simülasyon tamamlandı! Dashboard ve Model ağırlıkları otomatik güncellendi.\n")
    show_status()

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "simulate"
    if cmd == "status":
        show_status()
    elif cmd == "simulate":
        run_simulation()
    else:
        run_simulation()
