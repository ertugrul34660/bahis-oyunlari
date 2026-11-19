# -*- coding: utf-8 -*-
"""
Ertuğrul YZ - Önümüzdeki Program ve Tahminler Raporlayıcısı
Günün kalan saatlerindeki (14:00 - 23:59) tüm Maçkolik bültenini tarar,
v2.0.0-DeepLearned modeliyle tahminleri ve gerekçelerini listeler.
"""

import sys
import json
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from core.mackolik_harvester import MackolikHarvester
from core.adaptive_learner import AdaptiveLearner
from core.quant_sports_engine import calculate_expected_value

harvester = MackolikHarvester()
learner = AdaptiveLearner()

matches = harvester.fetch_live_program()
now = datetime.now()
current_minutes = now.hour * 60 + now.minute

def parse_match_time(m):
    s = m.get('saat', '99:99')
    try:
        parts = s.split(':')
        return int(parts[0]) * 60 + int(parts[1])
    except:
        return 9999

upcoming_today = []
for m in matches:
    t_min = parse_match_time(m)
    # 14:00 sonrasındaki maçlar
    if t_min >= current_minutes:
        upcoming_today.append((t_min, m))

upcoming_today.sort(key=lambda x: x[0])

print(f"Şu Anki Saat: {now.strftime('%H:%M')}")
print(f"Önümüzdeki Toplam Karşılaşma Sayısı: {len(upcoming_today)}")
print("=" * 80)

analyzed_program = []

for t_min, m in upcoming_today:
    odds = m.get("oranlar", {})
    ms1 = odds.get("ms_1", 0.0)
    msx = odds.get("ms_x", 0.0)
    ms2 = odds.get("ms_2", 0.0)
    alt25 = odds.get("alt_25", 0.0)
    ust25 = odds.get("ust_25", 0.0)

    if ms1 <= 1.05 or ms2 <= 1.05:
        continue

    saat = m.get("saat", "")
    lig = m.get("lig", "")
    ev = m.get("ev_sahibi", "")
    dep = m.get("deplasman", "")
    match_title = f"{ev} vs {dep}"

    is_cup = "Kupa" in lig or "Cup" in lig
    is_women = "(K)" in ev or "(K)" in dep or "Kadın" in lig

    # Özellik vektörleri
    h_feat = {"kadro": 0.8 if ms1 < 1.6 else (0.4 if ms1 > 3.0 else 0.6), "form": 0.65, "dinlenme": 0.8}
    a_feat = {"kadro": 0.8 if ms2 < 1.6 else (0.4 if ms2 > 3.0 else 0.6), "form": 0.60, "dinlenme": 0.6, "seyahat": 0.6 if is_cup else 0.2}

    pred = learner.predict_match(h_feat, a_feat, odds)
    pick = pred["secilen_bahis"]
    pick_odds = pred["oran"]
    conf = pred["guven_skoru"]

    calc_prob = pred["p_1"] if pick == "MS 1" else (pred["p_2"] if pick == "MS 2" else (pred["p_x"] if pick == "MS X" else 55.0))
    ev_alpha = calculate_expected_value(calc_prob, pick_odds)

    # RULE-01: Ağır favori tuzağı kontrolü
    if pick in ["MS 1", "MS 2"] and pick_odds < 1.50 and is_cup:
        not_str = "⚠️ Ağır Favori Tuzağı Riski (Kupa rotasyonu nedeniyle temkinli)"
    elif pick == "2.5 Alt" and is_women:
        not_str = "⚠️ Kadınlar Ligi Yüksek Pres Dikkati (RULE-02)"
    else:
        not_str = "✅ Model Güvenli Onay Verdi"

    analyzed_program.append({
        "saat": saat,
        "lig": lig,
        "mac": match_title,
        "secim": pick,
        "oran": pick_odds,
        "guven": conf,
        "ev_alpha": ev_alpha,
        "not": not_str
    })

print(f"Analiz Edilen Uygun Karşılaşma: {len(analyzed_program)}")
for p in analyzed_program[:12]:
    print(f"[{p['saat']}] {p['mac']:<35} | {p['lig'][:20]:<20}")
    print(f"   👉 Tahmin: {p['secim']:<8} (Oran: {p['oran']:.2f}) | Güven: %{p['guven']} | +EV: %{p['ev_alpha']:.1f} | {p['not']}")
    print("-" * 80)
