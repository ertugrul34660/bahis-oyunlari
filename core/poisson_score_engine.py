# -*- coding: utf-8 -*-
"""
Ertuğrul YZ - Poisson Dağılımı, Skor ve İlk Yarı Analiz Motoru (PoissonScoreEngine)
5. Kat Spor Analiz Laboratuvarı & Quant Modeli

Yetenekler:
1. Bivariate Poisson Dağılımı ile 0-0'dan 5-5'e kadar tüm kesin skor olasılıkları.
2. En olası kesin skor tahmini (Most Likely Exact Score).
3. İlk Yarı (İY 1, İY X, İY 2) ve İY 1.5 Alt/Üst olasılıkları.
4. Karşılıklı Gol (KG Var / KG Yok) olasılığı.
5. İlk Yarı / Maç Sonu (İY/MS) kombinasyonları (X/X, X/1, 1/1 vb.).
6. Toplam Gol (TG) aralıkları (0-1, 2-3, 4-6, 7+).
"""

import math
from typing import Dict, List, Any, Tuple

def poisson_prob(lmbda: float, k: int) -> float:
    """Poisson olasılık formülü: P(k) = (lambda^k * e^-lambda) / k!"""
    if lmbda <= 0:
        return 1.0 if k == 0 else 0.0
    return (math.pow(lmbda, k) * math.exp(-lmbda)) / math.factorial(k)


class PoissonScoreEngine:
    def __init__(self):
        pass

    def estimate_lambdas_from_odds(self, ms1: float, msx: float, ms2: float, alt25: float = 1.65, ust25: float = 2.0) -> Tuple[float, float]:
        """İddaa oranlarından ve 2.5 Alt/Üst verisinden takımların beklenen gollerini (lambda) çıkarır."""
        # Toplam beklenen gol (Total Expected Goals)
        if alt25 < ust25:
            # Düşük gollü maç (1.8 - 2.3 gol bandı)
            total_xg = 1.95 + (alt25 / 4.0)
        else:
            # Yüksek gollü maç (2.6 - 3.4 gol bandı)
            total_xg = 2.50 + (ust25 / 3.0)

        total_xg = max(1.5, min(3.8, total_xg))

        # Ev ve Deplasman oran ağırlığı
        inv1 = 1.0 / ms1 if ms1 > 0 else 0.5
        inv2 = 1.0 / ms2 if ms2 > 0 else 0.5
        tot_win = inv1 + inv2 or 1.0

        ratio_1 = inv1 / tot_win
        ratio_2 = inv2 / tot_win

        lambda_h = round(total_xg * ratio_1, 2)
        lambda_a = round(total_xg * ratio_2, 2)

        return lambda_h, lambda_a

    def calculate_full_analysis(self, home_team: str, away_team: str,
                                lambda_h: float, lambda_a: float, max_goals: int = 5) -> Dict[str, Any]:
        """Tüm skor matrisini, İY olasılıklarını ve alt/üst türevlerini hesaplar."""
        score_matrix = {}
        prob_over_25 = 0.0
        prob_btts = 0.0

        tg_0_1 = 0.0
        tg_2_3 = 0.0
        tg_4_6 = 0.0
        tg_7_plus = 0.0

        for h in range(max_goals + 1):
            for a in range(max_goals + 1):
                p_h = poisson_prob(lambda_h, h)
                p_a = poisson_prob(lambda_a, a)
                p_score = p_h * p_a
                score_matrix[(h, a)] = p_score

                # 2.5 Üst
                if (h + a) > 2.5:
                    prob_over_25 += p_score

                # KG Var
                if h > 0 and a > 0:
                    prob_btts += p_score

                # Toplam Gol
                tot_g = h + a
                if tot_g <= 1:
                    tg_0_1 += p_score
                elif tot_g in [2, 3]:
                    tg_2_3 += p_score
                elif tot_g in [4, 5, 6]:
                    tg_4_6 += p_score
                else:
                    tg_7_plus += p_score

        # En olası kesin skorlar
        sorted_scores = sorted(score_matrix.items(), key=lambda x: x[1], reverse=True)
        top_scores = [
            {"skor": f"{h}-{a}", "olasilik": round(p * 100, 1)}
            for (h, a), p in sorted_scores[:4]
        ]

        # -----------------------------------------------------------------
        # İLK YARI (İY) MODELİ: İlk yarı gol beklentisi maçın ~%43'üdür
        # -----------------------------------------------------------------
        ht_lambda_h = lambda_h * 0.43
        ht_lambda_a = lambda_a * 0.43

        ht_1 = 0.0
        ht_x = 0.0
        ht_2 = 0.0
        ht_under_15 = 0.0
        ht_scores = {}

        for h in range(4):
            for a in range(4):
                p_h = poisson_prob(ht_lambda_h, h)
                p_a = poisson_prob(ht_lambda_a, a)
                p_ht = p_h * p_a
                ht_scores[(h, a)] = p_ht

                if h > a:
                    ht_1 += p_ht
                elif h == a:
                    ht_x += p_ht
                else:
                    ht_2 += p_ht

                if (h + a) < 1.5:
                    ht_under_15 += p_ht

        # İY en olası skor
        sorted_ht = sorted(ht_scores.items(), key=lambda x: x[1], reverse=True)
        top_ht_score = f"{sorted_ht[0][0][0]}-{sorted_ht[0][0][1]}"

        # İY Tercihi
        if ht_x >= max(ht_1, ht_2) or abs(ht_1 - ht_2) < 0.10:
            best_ht_pick = "İY X"
            best_ht_prob = round(ht_x * 100, 1)
        elif ht_1 > ht_2:
            best_ht_pick = "İY 1"
            best_ht_prob = round(ht_1 * 100, 1)
        else:
            best_ht_pick = "İY 2"
            best_ht_prob = round(ht_2 * 100, 1)

        # İY/MS Kombinasyonu
        # Genelde en yaygın kupa ve kilit maç kalıbı: X/X, X/1, 1/1
        if best_ht_pick == "İY X":
            iyms_tahmin = "İY/MS X/1" if lambda_h > lambda_a * 1.3 else ("İY/MS X/2" if lambda_a > lambda_h * 1.3 else "İY/MS X/X")
        elif best_ht_pick == "İY 1":
            iyms_tahmin = "İY/MS 1/1"
        else:
            iyms_tahmin = "İY/MS 2/2"

        return {
            "mac": f"{home_team} vs {away_team}",
            "lambda_h": lambda_h,
            "lambda_a": lambda_a,
            "en_olasi_skor": top_scores[0]["skor"],
            "en_olasi_skor_yuzde": top_scores[0]["olasilik"],
            "alternatif_skorlar": top_scores[1:3],
            "ilk_yari_tahmini": best_ht_pick,
            "ilk_yari_guven": best_ht_prob,
            "ilk_yari_skor": top_ht_score,
            "ilk_yari_15_alt_yuzde": round(ht_under_15 * 100, 1),
            "kg_var_yuzde": round(prob_btts * 100, 1),
            "kg_yok_yuzde": round((1.0 - prob_btts) * 100, 1),
            "kg_tercihi": "KG VAR" if prob_btts >= 0.52 else "KG YOK",
            "iy_ms_tahmini": iyms_tahmin,
            "toplam_gol_araligi": "0-1 Gol" if tg_0_1 > 0.40 else ("2-3 Gol" if tg_2_3 > 0.45 else "4-6 Gol")
        }


# --- Test & Doğrulama ---
if __name__ == "__main__":
    engine = PoissonScoreEngine()
    print("=" * 65)
    print("🎯 ERTUĞRUL YZ - POISSON SKOR, İLK YARI & KG HESAPLAMA MOTORU")
    print("=" * 65)

    # Örnek: Lokomotiva Zvolen vs FK Kosice (Slovakya Kupa)
    lh, la = engine.estimate_lambdas_from_odds(ms1=7.01, msx=4.98, ms2=1.13, alt25=1.65, ust25=2.05)
    res = engine.calculate_full_analysis("Lokomotiva Zvolen", "FK Kosice", lh, la)

    print(f"🏟️ {res['mac']}")
    print(f"📊 Beklenen Goller: Ev: {res['lambda_h']} | Dep: {res['lambda_a']}")
    print(f"🎯 En Olası Skor: {res['en_olasi_skor']} (%{res['en_olasi_skor_yuzde']})")
    print(f"⏱️ İlk Yarı Tahmini: {res['ilk_yari_tahmini']} (%{res['ilk_yari_guven']}) | İY Skor: {res['ilk_yari_skor']}")
    print(f"🥅 İY 1.5 Alt Olasılığı: %{res['ilk_yari_15_alt_yuzde']}")
    print(f"🤝 Karşılıklı Gol: {res['kg_tercihi']} (Var: %{res['kg_var_yuzde']} | Yok: %{res['kg_yok_yuzde']})")
    print(f"🎲 İY/MS Kombinasyonu: {res['iy_ms_tahmini']}")
    print(f"⚽ Toplam Gol Aralığı: {res['toplam_gol_araligi']}")
    print("=" * 65)
