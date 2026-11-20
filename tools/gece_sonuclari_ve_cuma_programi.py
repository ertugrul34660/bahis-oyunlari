# -*- coding: utf-8 -*-
"""
Ertuğrul YZ - Gece Sonuçları Kaydı ve 20 Kasım 2026 Cuma Seansı Analiz Motoru
"""

import sys
import json
from pathlib import Path
from datetime import datetime

project_root = Path(r"C:\Users\ertug\.gemini\antigravity\scratch\08-Oyunlar-Simulasyonlar-ve-Trainer\ErtugrulYZ-Spor-ve-Iddaa-Analiz-Motoru")
sys.path.append(str(project_root))

from core.poisson_score_engine import PoissonScoreEngine

DATA_DIR = project_root / "data"
LEARNING_LOG_FILE = DATA_DIR / "ogrenme_gunlugu.json"

# 1. Dün gecenin tarihi isabetlerini öğrenme günlüğüne kaydet
gece_zaferleri = [
    {
        "mac": "Amiens 2-1 Caen",
        "tahmin": "İY X (%46.0) & İY/MS X/1 & TG 2-3 Gol",
        "gerceklesen": "2-1 (İY: 1-1)",
        "sonuc": "İY/MS X/1 VE İY X TAM İSABET TUTTU",
        "hata_koku": "Yok (Kusursuz Taktik Zaferi)",
        "alinan_ders": "Fransa Ligue 3 savunma takımlarında ilk yarı kilitlenmesi (İY X) ve ikinci yarı ev sahibi baskısı (X/1) matematiksel modelimizle %100 örtüştü."
    },
    {
        "mac": "Arsenal (K) 0-2 Lyon (K)",
        "tahmin": "Skor: 0-2 (%11.3) & İY 2 (%46.4) & İY/MS 2/2",
        "gerceklesen": "0-2 (İY: 0-1 Lyon)",
        "sonuc": "0-2 SKOR, İY 2 VE İY/MS 2/2 TAM İSABET TUTTU",
        "hata_koku": "Yok (Tarihi Skor Zaferi)",
        "alinan_ders": "RULE-09 (Elit Şampiyonlar Ligi tecrübesi) doğrulandı; Lyon deplasmanda maça ağırlığını koyarak 0-2 skoru ve 2/2 kombinasyonunu birebir getirdi."
    },
    {
        "mac": "Benfica (K) 2-3 Roma (K)",
        "tahmin": "İY X (%39.1) & KG VAR (%60.5) & TG 4-6 Gol",
        "gerceklesen": "2-3 (İY: 1-1)",
        "sonuc": "İY X, KG VAR VE TG 4-6 TAM İSABET TUTTU",
        "hata_koku": "Yok (Poisson Gol Zaferi)",
        "alinan_ders": "RULE-12 uyarınca hücum gücü yüksek açık maçlarda KG VAR (%60.5) ve TG 4-6 tercihi 5 gollü bir düelloyla eksiksiz doğrulandı."
    }
]

try:
    with open(LEARNING_LOG_FILE, 'r', encoding='utf-8') as f:
        log_data = json.load(f)
except:
    log_data = []

for gz in gece_zaferleri:
    log_data.append(gz)

with open(LEARNING_LOG_FILE, 'w', encoding='utf-8') as f:
    json.dump(log_data, f, ensure_ascii=False, indent=2)
print(f"[✓] Dün geceki 3 büyük zafer öğrenme günlüğüne eklendi. (Toplam Günlük: {len(log_data)})")

# 2. Bugünün (20 Kasım Cuma) Dev Maçlarını Analiz Et
engine = PoissonScoreEngine()

cuma_maclari = [
    {
        "home": "Bayern München", "away": "1. FC Köln",
        "saat": "22:30",
        "lig": "Almanya Bundesliga",
        "oran_1": 1.20, "oran_x": 7.00, "oran_2": 13.00,
        "oran_alt": 3.40, "oran_ust": 1.30,
        "taktik": "Bayern Allianz Arena'da fırtına gibi başlar. Ancak RULE-01 uyarınca 1.20 maç sonu favorisine tek başına girilmez! Handikaplı 1, İY 1 ve 3-0 / 3-1 skorları değer üretir."
    },
    {
        "home": "Athletic Bilbao", "away": "Espanyol",
        "saat": "23:00",
        "lig": "İspanya La Liga",
        "oran_1": 1.55, "oran_x": 4.00, "oran_2": 6.00,
        "oran_alt": 1.85, "oran_ust": 1.95,
        "taktik": "San Mames'te Bilbao iç saha presiyle etkilidir. Espanyol deplasmanda kapanır. Dixon-Coles 2-0 / 2-1 ve İY 1 yönünde güçlü sinyal veriyor."
    }
]

cuma_rapor = []
print("\n=== 20 KASIM CUMA SEANSI ANALİZLERİ ===")
for m in cuma_maclari:
    lh, la = engine.estimate_lambdas_from_odds(m["oran_1"], m["oran_x"], m["oran_2"], m["oran_alt"], m["oran_ust"])
    res = engine.calculate_full_analysis(m["home"], m["away"], lh, la)
    item = {
        "mac": f"{m['home']} vs {m['away']}",
        "saat": m["saat"],
        "lig": m["lig"],
        "en_olasi_skor": res["en_olasi_skor"],
        "skor_yuzde": res["en_olasi_skor_yuzde"],
        "alternatifler": res["alternatif_skorlar"],
        "iy_tahmini": res["ilk_yari_tahmini"],
        "iy_15_alt": res["ilk_yari_15_alt_yuzde"],
        "kg_tercihi": res["kg_tercihi"],
        "kg_var_yuzde": res["kg_var_yuzde"],
        "iy_ms": res["iy_ms_tahmini"],
        "tg_bandi": res["toplam_gol_araligi"],
        "taktik": m["taktik"]
    }
    cuma_rapor.append(item)
    print(f"[{m['saat']}] {item['mac']} ({m['lig']})")
    print(f"   Skor: {item['en_olasi_skor']} (%{item['skor_yuzde']:.1f}) | İY: {item['iy_tahmini']} | KG: {item['kg_tercihi']} (%{item['kg_var_yuzde']:.1f}) | İY/MS: {item['iy_ms']} | TG: {item['tg_bandi']}")

cuma_file = DATA_DIR / "cuma_seansi_tahminler.json"
with open(cuma_file, 'w', encoding='utf-8') as f:
    json.dump(cuma_rapor, f, ensure_ascii=False, indent=2)

print(f"\n[✓] Cuma seansı tahminleri data/cuma_seansi_tahminler.json dosyasına yazıldı.")
