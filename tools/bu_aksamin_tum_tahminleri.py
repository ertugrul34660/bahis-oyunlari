# -*- coding: utf-8 -*-
"""
Ertuğrul YZ - Bu Akşamın (20 Kasım Cuma) Tüm Çok Boyutlu Tahminleri ve Kadro Raporu
Dixon-Coles Poisson + Kadro İstihbarat Entegrasyonu
"""

import sys
import json
from pathlib import Path

project_root = Path(r"C:\Users\ertug\.gemini\antigravity\scratch\08-Oyunlar-Simulasyonlar-ve-Trainer\ErtugrulYZ-Spor-ve-Iddaa-Analiz-Motoru")
sys.path.append(str(project_root))

from core.poisson_score_engine import PoissonScoreEngine
from core.squad_investigator import SquadInvestigator, KadroRaporu

engine = PoissonScoreEngine()
investigator = SquadInvestigator()

aksam_bulteni = [
    {
        "home": "Bayern München", "away": "1. FC Köln",
        "saat": "22:30", "lig": "Almanya Bundesliga",
        "oran_1": 1.20, "oran_x": 7.00, "oran_2": 13.00,
        "oran_alt": 3.40, "oran_ust": 1.30,
        "home_squad": "Urbig, Laimer, Upamecano, Tah, Stanisic, Kimmich, Pavlovic, Olise, Karl, Harry Kane",
        "away_squad": "Schwabe, Sebulonsen, Schmied, Simpson-Pusey, Sosa, Krauss, Maina, Moore, Bülter, El Mala",
        "sakatlar_home": "Neuer, Davies, Gnabry",
        "sakatlar_away": "Hübers, Skhiri, Dallinga",
        "taktik_ozet": "Harry Kane ve Olise ilk 11'de. Neuer yok ama Urbig eski takımına karşı ekstra konsantre. RULE-01 gereği 1.20 maç sonu pas geçilir; İY 1 (%54) ve 2-0 / 3-0 handikaplı skorlar değerlidir."
    },
    {
        "home": "Athletic Bilbao", "away": "Espanyol",
        "saat": "23:00", "lig": "İspanya La Liga",
        "oran_1": 1.55, "oran_x": 4.00, "oran_2": 6.00,
        "oran_alt": 1.85, "oran_ust": 1.95,
        "home_squad": "Unai Simon, Rincón, Laporte, Yuri, Ruiz de Galarreta, Sancet, Berenguer, Inaki Williams, Nico Williams",
        "away_squad": "Fortuno, El Hilali, Cabrera, Hartman, Santiago, Lozano, Moscardo, Pere Milla, Roberto",
        "sakatlar_home": "Yok (Tam forvet hattı)",
        "sakatlar_away": "Yeni teknik direktör Eder Sarabia ilk maçında",
        "taktik_ozet": "Nico ve Inaki Williams kanatlarda, Sancet 10 numarada tam güç! San Mames'te iç saha baskısı çok yüksektir; Espanyol deplasman kısırlığı yaşar. 2-0 / 1-0 ve İY 1 güçlüdür."
    },
    {
        "home": "Clermont Foot", "away": "FC Metz",
        "saat": "21:00", "lig": "Fransa Ligue 2",
        "oran_1": 3.10, "oran_x": 3.00, "oran_2": 2.35,
        "oran_alt": 1.60, "oran_ust": 2.15,
        "home_squad": "Guivarch, Da Silva, Konate, Armougom, Gastien, Keita, Saivet, Douane, Bassouamina",
        "away_squad": "Oukidja, Kouao, Traore, Cande, Udol, Deminguet, Stambouli, Jallow, Hein, Sabaly",
        "sakatlar_home": "Defansta rotasyon",
        "sakatlar_away": "Tam kadro zirve takibi",
        "taktik_ozet": "Fransa 2. lig klasiği. İki denk takımın savunma temkini ilk yarıyı kilitler. İY X (%47.2) ve 1-1 / 0-1 skorları öne çıkar."
    },
    {
        "home": "Nancy", "away": "Dijon",
        "saat": "21:00", "lig": "Fransa Ligue 2",
        "oran_1": 2.25, "oran_x": 2.95, "oran_2": 3.30,
        "oran_alt": 1.55, "oran_ust": 2.25,
        "home_squad": "Sourzac, Bussmann, Pellegrini, Mendy, Carlier, Bouriaud, Camara, Touré, Cissé",
        "away_squad": "Delecroix, Makutungu, Drouhin, Bernard, Marié, Chahid, Vargas, Schur, Duville-Parmentier",
        "sakatlar_home": "Yok",
        "sakatlar_away": "Orta sahada eksikler",
        "taktik_ozet": "Ligin en az gol yiyen savunmalarından ikisi. 2.5 Alt (%64.0) ve İY X beraberlik kilidi en yüksek matematiksel olasılığa sahiptir."
    }
]

sonuclar = []
for m in aksam_bulteni:
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
        "home_squad": m["home_squad"],
        "away_squad": m["away_squad"],
        "sakatlar": f"Ev: {m['sakatlar_home']} | Dep: {m['sakatlar_away']}",
        "taktik_ozet": m["taktik_ozet"]
    }
    sonuclar.append(item)

out_file = project_root / "data" / "bu_aksamin_tum_tahminleri.json"
with open(out_file, "w", encoding="utf-8") as f:
    json.dump(sonuclar, f, ensure_ascii=False, indent=2)

print(f"[✓] {len(sonuclar)} maçlık akşam seansı çok boyutlu tahminleri kaydedildi.")
