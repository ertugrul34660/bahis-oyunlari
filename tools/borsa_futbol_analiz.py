# -*- coding: utf-8 -*-
"""
Ertuğrul YZ - Borsa ve Kantitatif Finans Destekli Maç Analiz Aracı
Kullanım:
    python borsa_futbol_analiz.py
    python borsa_futbol_analiz.py "Badajoz" "Tenerife"
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from core.quant_sports_engine import run_quant_match_screen

def analyze_match_with_quant(home="CD Badajoz", away="CD Tenerife"):
    print("\n" + "=" * 70)
    print("📈 ERTUĞRUL YZ - KANTİTATİF BORSA & FUTBOL TİCARET TERMİNALİ")
    print(f"🏟️ Karşılaşma: {home} vs {away}")
    print("=" * 70)

    # Badajoz & Tenerife Kantitatif Verileri
    home_form = ["G", "B", "G", "M", "G"]
    home_gd = [1, 0, 2, -1, 1]

    away_form = ["M", "B", "G", "B", "M"]
    away_gd = [-2, 0, 1, 0, -1]

    recent_goals = [1, 2, 0, 2, 1, 3, 1]  # İki takımın son kupa/lig gol sayıları

    model_probs = {
        "MS 1": 19.5,
        "MS X": 25.8,
        "MS 2": 54.7,
        "2.5 Alt": 64.5
    }

    odds = {
        "ms_1": 4.44,
        "ms_x": 3.36,
        "ms_2": 1.47,
        "alt_25": 1.55
    }

    quant_res = run_quant_match_screen(
        home_name=home,
        away_name=away,
        home_form=home_form,
        home_gd=home_gd,
        away_form=away_form,
        away_gd=away_gd,
        recent_goals_combined=recent_goals,
        model_probs=model_probs,
        odds=odds,
        bankroll=10000.0
    )

    print("\n📊 1) BORSA TEKNİK İNDİKATÖRLERİ (FUTBOL RSI & VOLATİLİTE)")
    print("-" * 70)
    print(f"• {home:<15} Form RSI : {quant_res['home_rsi']} / 100")
    print(f"• {away:<15} Form RSI : {quant_res['away_rsi']} / 100")
    vol = quant_res["volatilite"]
    print(f"• Skor Volatilitesi     : {vol['durum']}")
    print(f"• Ortalama Gol / Sapma : {vol['mean_goals']} gol (±{vol['std_dev']}) | Bollinger: [{vol['lower_band']} - {vol['upper_band']}]")

    if quant_res["sinyaller"]:
        print("\n⚡ Borsa İndikatör Sinyalleri:")
        for s in quant_res["sinyaller"]:
            print(f"  {s}")

    print("\n🎯 2) KANTİTATİF DEĞER (+EV ALPHA) & KELLY PORTFÖY DAĞILIMI")
    print("-" * 70)
    print(f"• Piyasa Öneri / Seçim : {quant_res['en_iyi_market']} (İddaa Oranı: {quant_res['en_iyi_oran']:.2f})")
    print(f"• Model Gerçek İhtimal : %{quant_res['model_olasiligi']}")
    print(f"• Beklenen Değer (+EV) : %{quant_res['beklenen_deger_ev']:+0.2f} (Matematiksel Getiri Avantajı)")
    print(f"• Kelly Optimal Pozisyon: {quant_res['kelly_tutar']:.2f} TL (Kasa Riski: %{quant_res['kelly_tutar']/100:.1f})")
    print(f"• Finansal Karar / Emir: 🚀 {quant_res['finansal_aksiyon']}")

    print("\n🛡️ 3) HEDGING & RİSKTEN KORUNMA TÜREVİ")
    print("-" * 70)
    print(f"• {quant_res['hedging_tavsiyesi']}")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    h = sys.argv[1] if len(sys.argv) > 1 else "CD Badajoz"
    a = sys.argv[2] if len(sys.argv) > 2 else "CD Tenerife"
    analyze_match_with_quant(h, a)
