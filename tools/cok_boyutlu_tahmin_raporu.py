# -*- coding: utf-8 -*-
"""
Ertuğrul YZ - Çok Boyutlu Maç, Kesin Skor, İlk Yarı ve KG Analiz Raporlayıcısı
Günün maçları için Poisson dağılımı ile kesin skor, ilk yarı ve KG analizlerini hesaplar.
"""

import sys
import json
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from core.poisson_score_engine import PoissonScoreEngine
from tools.github_yukle import push_to_github

engine = PoissonScoreEngine()

# Bugünün kritik maçları ve oranları
MATCHES_DATA = [
    {
        "saat": "15:00",
        "lig": "Slovakya Kupa Son 16",
        "ev": "Lokomotiva Zvolen",
        "dep": "FK Kosice",
        "oranlar": {"ms1": 7.01, "msx": 4.98, "ms2": 1.13, "alt": 1.65, "ust": 2.05}
    },
    {
        "saat": "15:00",
        "lig": "AFC ASEAN Kulüpler Şampiyonası",
        "ev": "Svay Rieng",
        "dep": "Port FC",
        "oranlar": {"ms1": 3.10, "msx": 3.35, "ms2": 2.05, "alt": 1.86, "ust": 1.74}
    },
    {
        "saat": "15:30",
        "lig": "Slovenya Kupa Son 16",
        "ev": "Dob",
        "dep": "Bistrica",
        "oranlar": {"ms1": 3.94, "msx": 3.36, "ms2": 1.47, "alt": 1.84, "ust": 1.76}
    },
    {
        "saat": "15:30",
        "lig": "Slovenya Kupa Son 16",
        "ev": "Beltinci",
        "dep": "Celje",
        "oranlar": {"ms1": 5.79, "msx": 4.22, "ms2": 1.21, "alt": 1.65, "ust": 2.05}
    },
    {
        "saat": "16:00",
        "lig": "İran Persian Gulf Pro Lig",
        "ev": "Malavan",
        "dep": "Gol Gohar Sirjan",
        "oranlar": {"ms1": 2.36, "msx": 2.40, "ms2": 2.52, "alt": 1.40, "ust": 2.45}
    },
    {
        "saat": "20:45",
        "lig": "UEFA Kadınlar Şampiyonlar Ligi",
        "ev": "Paris (K)",
        "dep": "Koge (K)",
        "oranlar": {"ms1": 1.36, "msx": 3.73, "ms2": 4.09, "alt": 1.95, "ust": 1.68}
    },
    {
        "saat": "22:45",
        "lig": "Fransa Ligue 3",
        "ev": "Amiens",
        "dep": "Caen",
        "oranlar": {"ms1": 1.95, "msx": 2.83, "ms2": 2.67, "alt": 1.60, "ust": 2.10}
    },
    {
        "saat": "23:00",
        "lig": "UEFA Kadınlar Şampiyonlar Ligi",
        "ev": "Arsenal (K)",
        "dep": "Lyon (K)",
        "oranlar": {"ms1": 3.65, "msx": 3.50, "ms2": 1.48, "alt": 2.13, "ust": 1.55}
    },
    {
        "saat": "23:00",
        "lig": "UEFA Kadınlar Şampiyonlar Ligi",
        "ev": "Benfica (K)",
        "dep": "Roma (K)",
        "oranlar": {"ms1": 1.81, "msx": 3.30, "ms2": 2.62, "alt": 1.85, "ust": 1.75}
    }
]


def run_multi_dimensional_predictions():
    print("=" * 85)
    print("🎯 ERTUĞRUL YZ - ÇOK BOYUTLU İDDAA, KESİN SKOR & İLK YARI RAPORU")
    print("=" * 85)

    results = []

    for m in MATCHES_DATA:
        o = m["oranlar"]
        lh, la = engine.estimate_lambdas_from_odds(o["ms1"], o["msx"], o["ms2"], o["alt"], o["ust"])
        res = engine.calculate_full_analysis(m["ev"], m["dep"], lh, la)
        res["saat"] = m["saat"]
        res["lig"] = m["lig"]
        results.append(res)

        print(f"\n⚽ [{res['saat']}] {res['mac']} ({res['lig']})")
        print(f"   • Beklenen Goller: Ev: {res['lambda_h']} | Dep: {res['lambda_a']}")
        print(f"   • 🎯 En Olası Skor: {res['en_olasi_skor']} (%{res['en_olasi_skor_yuzde']}) | Alternatif: {res['alternatif_skorlar'][0]['skor']} (%{res['alternatif_skorlar'][0]['olasilik']})")
        print(f"   • ⏱️ İlk Yarı (İY): {res['ilk_yari_tahmini']} (%{res['ilk_yari_guven']}) | İY Skor: {res['ilk_yari_skor']} | İY 1.5 Alt: %{res['ilk_yari_15_alt_yuzde']}")
        print(f"   • 🤝 Karşılıklı Gol: {res['kg_tercihi']} (Var: %{res['kg_var_yuzde']} | Yok: %{res['kg_yok_yuzde']})")
        print(f"   • 🎲 İY/MS Kombini : {res['iy_ms_tahmini']}")
        print(f"   • 🥅 Toplam Gol    : {res['toplam_gol_araligi']}")

    # JSON Olarak Kaydet
    out_file = project_root / "data" / "cok_boyutlu_tahminler.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 85)
    print(f"[✓] Tüm çok boyutlu skor ve İY analizleri kaydedildi: {out_file}")

    # GitHub'a senkronize et
    print("\n[*] GitHub deposu güncelleniyor...")
    try:
        push_to_github()
    except Exception as e:
        print(f"[!] GitHub notu: {e}")

    return results


if __name__ == "__main__":
    run_multi_dimensional_predictions()
