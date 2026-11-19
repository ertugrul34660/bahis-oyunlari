# -*- coding: utf-8 -*-
"""
Ertuğrul YZ - Akşam Seansı Master Analiz ve Taktik Raporu (v2.1.0-MasterLearned)
Yeni öğrenilen kurallar ışığında akşam maçlarını analiz eder.
"""

import sys
from pathlib import Path
import json

project_root = Path(r"C:\Users\ertug\.gemini\antigravity\scratch\08-Oyunlar-Simulasyonlar-ve-Trainer\ErtugrulYZ-Spor-ve-Iddaa-Analiz-Motoru")
sys.path.append(str(project_root))
DATA_DIR = project_root / "data"

from core.poisson_score_engine import PoissonScoreEngine

engine = PoissonScoreEngine()

aksam_maclari = [
    {
        "home": "Paris (K)", "away": "Koge (K)",
        "saat": "20:45",
        "lig": "UEFA Kadınlar Şampiyonlar Ligi",
        "oran_1": 1.25, "oran_x": 5.50, "oran_2": 9.50,
        "oran_alt": 2.60, "oran_ust": 1.45,
        "taktiksel_not": "Paris iç sahada yüksek hücum temposuna sahip. Koge savunmada açık veriyor. RULE-02 uyarınca 2.5 Alt tuzağından kaçınıldı; ev sahibi farkı ve 2-0 / 3-0 skoru ön planda."
    },
    {
        "home": "Amiens", "away": "Caen",
        "saat": "22:45",
        "lig": "Fransa Ligue 3",
        "oran_1": 2.20, "oran_x": 3.00, "oran_2": 3.10,
        "oran_alt": 1.60, "oran_ust": 2.15,
        "taktiksel_not": "Fransa alt ligi katı savunma disiplini. RULE-11 gereğince 1-0 / 1-1 skorları ve İY X beraberlik katsayısı (%46+) en güvenli limandır."
    },
    {
        "home": "Arsenal (K)", "away": "Lyon (K)",
        "saat": "23:00",
        "lig": "UEFA Kadınlar Şampiyonlar Ligi",
        "oran_1": 3.20, "oran_x": 3.60, "oran_2": 1.95,
        "oran_alt": 2.10, "oran_ust": 1.65,
        "taktiksel_not": "Avrupa kadın futbolunun iki devi. Lyon Şampiyonlar Ligi tecrübesiyle (RULE-09) deplasmanda avantajlı. Poisson 0-2 / 1-2 deplasman üstünlüğü öngörüyor."
    },
    {
        "home": "Benfica (K)", "away": "Roma (K)",
        "saat": "23:00",
        "lig": "UEFA Kadınlar Şampiyonlar Ligi",
        "oran_1": 2.40, "oran_x": 3.40, "oran_2": 2.60,
        "oran_alt": 2.05, "oran_ust": 1.70,
        "taktiksel_not": "İki hücum takımı. RULE-12 uyarınca karşılıklı goller kaçınılmaz; KG VAR (%59.1) ve 1-1 / 2-1 skorları en yüksek matematiksel beklentiye sahiptir."
    }
]

print("=== AKŞAM SEANSI MASTER TAHMİNLER (v2.1.0) ===")
rapor = []
for m in aksam_maclari:
    lh, la = engine.estimate_lambdas_from_odds(m["oran_1"], m["oran_x"], m["oran_2"], m["oran_alt"], m["oran_ust"])
    p_res = engine.calculate_full_analysis(m["home"], m["away"], lh, la)
    
    m_data = {
        "mac": f"{m['home']} vs {m['away']}",
        "saat": m["saat"],
        "lig": m["lig"],
        "lambda_h": p_res["lambda_h"],
        "lambda_a": p_res["lambda_a"],
        "en_olasi_skor": p_res["en_olasi_skor"],
        "skor_olasilik": p_res["en_olasi_skor_yuzde"],
        "alternatif_skorlar": p_res["alternatif_skorlar"],
        "iy_tahmini": p_res["ilk_yari_tahmini"],
        "iy_guven": p_res["ilk_yari_guven"],
        "iy_15_alt": p_res["ilk_yari_15_alt_yuzde"],
        "kg_tercihi": p_res["kg_tercihi"],
        "kg_var_yuzde": p_res["kg_var_yuzde"],
        "iy_ms": p_res["iy_ms_tahmini"],
        "tg_bandi": p_res["toplam_gol_araligi"],
        "taktiksel_not": m["taktiksel_not"]
    }
    rapor.append(m_data)
    print(f"\n[{m['saat']}] {m['home']} vs {m['away']} ({m['lig']})")
    print(f"   Skor: {p_res['en_olasi_skor']} (%{p_res['en_olasi_skor_yuzde']:.1f}) | İY: {p_res['ilk_yari_tahmini']} | KG: {p_res['kg_tercihi']} (%{p_res['kg_var_yuzde']:.1f}) | İY/MS: {p_res['iy_ms_tahmini']} | TG: {p_res['toplam_gol_araligi']}")
    print(f"   Taktiksel Not: {m['taktiksel_not']}")

output_file = DATA_DIR / "aksam_seansi_master_tahminler.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(rapor, f, ensure_ascii=False, indent=2)

print("\n[✓] Akşam seansı master tahminleri data/aksam_seansi_master_tahminler.json dosyasına kaydedildi.")
