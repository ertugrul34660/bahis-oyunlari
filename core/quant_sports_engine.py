# -*- coding: utf-8 -*-
"""
Ertuğrul YZ - Kantitatif Borsa ve Futbol Entegrasyon Motoru (Quant Sports Engine)
2. Kat Finans & Borsa ilkelerini 5. Kat Spor Analiz Motoru'na entegre eder.

Borsa İndikatörleri:
- Takım Form RSI (Aşırı Alım / Aşırı Satım)
- Skor Volatilitesi & Bollinger Bantları
- Beklenen Değer (+EV Alpha Generation)
- Kelly Kriteri Dinamik Pozisyon Boyutlandırma (Position Sizing)
- Finansal Hedging (Sigorta / Korunma)
"""

import math
from typing import Dict, List, Any, Tuple

def calculate_team_rsi(form_results: List[str], goal_diffs: List[int]) -> float:
    """
    Borsa RSI göstergesini futbol takımının son 5-10 maçına uyarlar (0 - 100 arası).
    Sonuçlar: 'G' (Galibiyet), 'B' (Beraberlik), 'M' (Mağlubiyet)
    goal_diffs: Her maçtaki gol farkı (+2, 0, -1 vb.)
    """
    if not form_results:
        return 50.0

    gains = []
    losses = []

    for r, gd in zip(form_results, goal_diffs):
        if r == "G":
            gains.append(3.0 + max(0, gd))
            losses.append(0.0)
        elif r == "B":
            gains.append(1.0)
            losses.append(1.0)
        else:
            gains.append(0.0)
            losses.append(3.0 + abs(min(0, gd)))

    avg_gain = sum(gains) / len(gains) if gains else 0.0
    avg_loss = sum(losses) / len(losses) if losses else 0.0

    if avg_loss == 0.0:
        return 100.0 if avg_gain > 0 else 50.0

    rs = avg_gain / avg_loss
    rsi = 100.0 - (100.0 / (1.0 + rs))
    return round(rsi, 1)


def calculate_volatility(recent_total_goals: List[int]) -> Dict[str, Any]:
    """
    Bollinger Bantları mantığıyla toplam gol volatilitesini hesaplar.
    Düşük oynaklık: 2.5 Alt için ideal zemin.
    Yüksek oynaklık: KG Var & 2.5 Üst için ideal zemin.
    """
    if not recent_total_goals:
        return {"mean": 2.5, "std_dev": 0.5, "durum": "NORMAL", "bant_araligi": "1.8 - 3.2"}

    n = len(recent_total_goals)
    mean = sum(recent_total_goals) / n
    variance = sum((x - mean) ** 2 for x in recent_total_goals) / max(1, n - 1)
    std_dev = math.sqrt(variance)

    lower_band = max(0.0, mean - (1.5 * std_dev))
    upper_band = mean + (1.5 * std_dev)

    if std_dev < 0.7:
        durum = "DÜŞÜK VOLATİLİTE (Defansif / 2.5 Alt Eğilimli)"
    elif std_dev > 1.3:
        durum = "YÜKSEK VOLATİLİTE (Açık Futbol / KG Var & 2.5 Üst Eğilimli)"
    else:
        durum = "DENGELİ VOLATİLİTE"

    return {
        "mean_goals": round(mean, 2),
        "std_dev": round(std_dev, 2),
        "lower_band": round(lower_band, 1),
        "upper_band": round(upper_band, 1),
        "durum": durum
    }


def calculate_expected_value(prob_pct: float, odds: float) -> float:
    """
    Borsa Beklenen Değer (+EV / Alpha):
    EV = (Olasılık * Net Kâr) - ((1 - Olasılık) * Risk Edilen Anapara)
    Pozitif EV = Piyasanın sunduğu fiyatta matematiksel avantaj (Iskonto).
    """
    if odds <= 1.0:
        return -100.0
    p = prob_pct / 100.0
    q = 1.0 - p
    net_win = odds - 1.0
    ev = (p * net_win) - (q * 1.0)
    return round(ev * 100.0, 2)


def calculate_kelly_stake(bankroll: float, prob_pct: float, odds: float, fraction: float = 0.25, max_cap: float = 0.04) -> float:
    """
    Wall Street / Jane Street Kelly Criterion Portföy Pozisyon Boyutlandırması.
    f* = (b*p - q) / b
    fraction: %25 Fractional Kelly (Sermaye koruma ve batmama zırhı)
    max_cap: Tek bahiste kasa maksimum %4 risk edilir.
    """
    if odds <= 1.0:
        return 0.0

    p = prob_pct / 100.0
    q = 1.0 - p
    b = odds - 1.0

    f_star = (b * p - q) / b

    if f_star <= 0:
        return 0.0  # Negatif beklentide işlem açılmaz

    # Fractional Kelly koruması
    optimal_fraction = min(max_cap, f_star * fraction)
    stake = round(bankroll * optimal_fraction, 2)
    return max(50.0, stake) if optimal_fraction > 0.005 else 0.0


def run_quant_match_screen(home_name: str, away_name: str,
                           home_form: List[str], home_gd: List[int],
                           away_form: List[str], away_gd: List[int],
                           recent_goals_combined: List[int],
                           model_probs: Dict[str, float],
                           odds: Dict[str, float],
                           bankroll: float = 10000.0) -> Dict[str, Any]:
    """
    Bir futbol maçına Wall Street kantitatif borsa taraması uygular.
    """
    home_rsi = calculate_team_rsi(home_form, home_gd)
    away_rsi = calculate_team_rsi(away_form, away_gd)
    volatility = calculate_volatility(recent_goals_combined)

    # Her market için Beklenen Değer (+EV) hesabı
    ev_ms1 = calculate_expected_value(model_probs.get("MS 1", 33.3), odds.get("ms_1", 2.0))
    ev_msx = calculate_expected_value(model_probs.get("MS X", 33.3), odds.get("ms_x", 3.2))
    ev_ms2 = calculate_expected_value(model_probs.get("MS 2", 33.3), odds.get("ms_2", 2.2))
    ev_alt = calculate_expected_value(model_probs.get("2.5 Alt", 50.0), odds.get("alt_25", 1.8))

    ev_dict = {
        "MS 1": (ev_ms1, odds.get("ms_1", 2.0), model_probs.get("MS 1", 33.3)),
        "MS X": (ev_msx, odds.get("ms_x", 3.2), model_probs.get("MS X", 33.3)),
        "MS 2": (ev_ms2, odds.get("ms_2", 2.2), model_probs.get("MS 2", 33.3)),
        "2.5 Alt": (ev_alt, odds.get("alt_25", 1.8), model_probs.get("2.5 Alt", 50.0))
    }

    # En yüksek pozitif EV'ye sahip piyasa
    best_market = max(ev_dict, key=lambda k: ev_dict[k][0])
    best_ev, best_odd, best_prob = ev_dict[best_market]

    # Kelly Kriteriyle Optimal Yatırım
    if best_ev > 0:
        recommended_stake = calculate_kelly_stake(bankroll, best_prob, best_odd)
        action = "GÜÇLÜ ALIM (LONG POZİSYON)" if best_ev > 12.0 else "DEĞER ALIMI (+EV LONG)"
    else:
        recommended_stake = 0.0
        action = "PAS GEÇ (NEGATİF BEKLENTİ / EDGE YOK)"

    # Borsa İndikatör Sinyalleri
    signals = []
    if home_rsi > 75:
        signals.append(f"⚠️ {home_name} RSI ({home_rsi}) AŞIRI ALIM BÖLGESİNDE: Fiyat/oran aşırı düşmüş, piyasa takımı abartıyor olabilir.")
    elif home_rsi < 25:
        signals.append(f"💡 {home_name} RSI ({home_rsi}) AŞIRI SATIM BÖLGESİNDE: Tepki yükselişi potansiyeli yüksek, kelepir oran fırsatı.")

    if away_rsi > 75:
        signals.append(f"⚠️ {away_name} RSI ({away_rsi}) AŞIRI ALIM: Deplasman takımı bültende aşırı şişirilmiş.")
    elif away_rsi < 25:
        signals.append(f"💡 {away_name} RSI ({away_rsi}) AŞIRI SATIM: Deplasman sürprizi için yüksek çarpan değeri.")

    # Finansal Hedging Tavsiyesi
    hedging_advice = "Gerek yok (Tekli pozisyon yeterli)."
    if best_market in ["MS 1", "MS 2"] and model_probs.get("MS X", 0) > 25.0:
        hedge_option = "1-X Çifte Şans" if best_market == "MS 1" else "X-2 Çifte Şans"
        hedging_advice = f"Opsiyonel Hedging: Beraberlik riski yüksek (%{model_probs.get('MS X')}). Sermaye koruma için '{hedge_option}' veya DNB (Beraberlikte İade) ile korunmalı alım önerilir."

    return {
        "home_rsi": home_rsi,
        "away_rsi": away_rsi,
        "volatilite": volatility,
        "en_iyi_market": best_market,
        "en_iyi_oran": best_odd,
        "beklenen_deger_ev": best_ev,
        "model_olasiligi": best_prob,
        "kelly_tutar": recommended_stake,
        "finansal_aksiyon": action,
        "sinyaller": signals,
        "hedging_tavsiyesi": hedging_advice
    }
