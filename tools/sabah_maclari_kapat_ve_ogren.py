# -*- coding: utf-8 -*-
"""
Ertuğrul YZ - Sabah Maçları Sonuçlandırma ve Hata Otopsisi
1. Queensland Lions 1-1 Wollongong Wolves (MS 1 kayıp)
2. Omiya Ardija 3-0 INAC Kobe (2.5 Alt kayıp)
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from core.sqlite_bankroll_manager import AutonomousBankrollManager
from core.adaptive_learner import AdaptiveLearner
from ui.mackolik_robot_dashboard_generator import generate_mackolik_dashboard_html

mgr = AutonomousBankrollManager()
learner = AdaptiveLearner()

print("=" * 70)
print("🔍 19 KASIM SABAH MAÇLARI CANLI SAHA SONUÇLANDIRMASI")
print("=" * 70)

# 1. Bet #9 Çözümle
# Tahmin: MS 1 | Gerçek: MS X (1-1 Bitti)
res9 = mgr.resolve_bet(bet_id=9, won=False, odds=1.44)
print(f"[❌] Kupon #9 Kapatıldı: Queensland Lions 1-1 Wollongong | Kayıp: 150.00 TL")

# 2. Bet #10 Çözümle
# Tahmin: 2.5 Alt | Gerçek: 2.5 Üst (3-0 Bitti)
res10 = mgr.resolve_bet(bet_id=10, won=False, odds=1.67)
print(f"[❌] Kupon #10 Kapatıldı: Omiya 3-0 INAC Kobe | Kayıp: 150.00 TL")

# 3. Kök Neden Otopsisi ve Öz-Öğrenme
print("\n[🧠 ÖZ-ÖĞRENME & KÖK NEDEN OTOPSİSİ BAŞLATILDI]")
print("-" * 70)

l9 = learner.learn_from_result(
    match_name="Queensland Lions vs Wollongong Wolves",
    predicted_pick="MS 1",
    actual_result="MS X",
    home_feat={"kadro": 0.65, "form": 0.60, "dinlenme": 0.8},
    away_feat={"kadro": 0.50, "form": 0.55, "dinlenme": 0.7, "seyahat": 0.3}
)
print("  📌 Queensland Lions 1-1 Wollongong:")
print(f"     🔍 Kök Neden : {l9['hata_koku']}")
print(f"     📚 Alınan Ders: {l9['alinan_ders']}")

l10 = learner.learn_from_result(
    match_name="Omiya Ardija (K) vs INAC Kobe (K)",
    predicted_pick="2.5 Alt",
    actual_result="2.5 Üst",
    home_feat={"kadro": 0.50, "form": 0.65, "dinlenme": 0.7},
    away_feat={"kadro": 0.70, "form": 0.70, "dinlenme": 0.6, "seyahat": 0.2}
)
print("  📌 Omiya Ardija 3-0 INAC Kobe:")
print(f"     🔍 Kök Neden : {l10['hata_koku']}")
print(f"     📚 Alınan Ders: {l10['alinan_ders']}")

print("\n📈 Güncellenen Karar Katsayıları:")
for k, v in learner.weights.get("agirliklar", {}).items():
    k_clean = k.replace("_", " ").title()
    print(f"   • {k_clean:<26}: %{v*100:.1f}")

# 4. Kasa ve KPI Raporu
kpis = mgr.get_kpi_summary()
print("\n" + "=" * 70)
print(f"💰 Nakit Kasa Rezervi : {kpis['guncel_kasa']:,.2f} TL")
print(f"📊 Net Toplam Kâr    : {kpis['net_kar_zarar']:+,.2f} TL (ROI: %{kpis['roi_yuzde']})")
print(f"🎯 Başarı Oranı      : %{kpis['basari_orani_yuzde']} ({kpis['kazanan_bahis']}W / {kpis['kaybeden_bahis']}L)")
print(f"⏳ Kalan Bekleyen    : {kpis['bekleyen_bahis']} Adet (15:00 ve 15:30 Maçları)")
print("=" * 70)

# 5. Dashboard güncelle
try:
    html = generate_mackolik_dashboard_html()
    with open(project_root / "ui" / "mackolik_robot_dashboard.html", "w", encoding="utf-8") as f:
        f.write(html)
except Exception as e:
    pass
