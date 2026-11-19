# -*- coding: utf-8 -*-
"""
Ertuğrul YZ - Otonom Canlı Maç Analiz ve Bahis Motoru
Bugünkü en yakın maçları tarar, Quant modelleriyle analiz eder,
Kelly kriteriyle pozisyon açar ve SQLite veritabanına PENDING olarak kaydeder.
"""

import sys
import json
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from core.mackolik_harvester import MackolikHarvester
from core.adaptive_learner import AdaptiveLearner
from core.risk_guardian import RiskGuardian
from core.quant_sports_engine import (
    calculate_team_rsi, calculate_volatility,
    calculate_expected_value, calculate_kelly_stake
)
from core.sqlite_bankroll_manager import AutonomousBankrollManager
from ui.mackolik_robot_dashboard_generator import generate_mackolik_dashboard_html

DATA_DIR = project_root / "data"
ROBOT_STATE_FILE = DATA_DIR / "mackolik_robot_durumu.json"


def parse_match_time(m):
    s = m.get('saat', '99:99')
    try:
        parts = s.split(':')
        return int(parts[0]) * 60 + int(parts[1])
    except:
        return 9999


def run_autonomous_betting_session():
    print("=" * 75)
    print("🤖 ERTUĞRUL YZ - OTONOM SPOR & İDDAA ANALİZ MOTORU ÇALIŞTIRILIYOR")
    print("=" * 75)

    harvester = MackolikHarvester()
    learner = AdaptiveLearner()
    guardian = RiskGuardian(max_daily_loss_pct=0.10)
    bankroll_mgr = AutonomousBankrollManager()

    current_kasa = bankroll_mgr.get_current_balance()
    print(f"💰 Güncel SQLite Kasa Bakiyesi: {current_kasa:,.2f} TL")
    print(f"⏰ Çalışma Zamanı: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 1. Devre Kesici Kontrolü
    is_locked, lock_reason = guardian.check_circuit_breaker(current_kasa)
    if is_locked:
        print(f"[🛡️ DEVRE KESİCİ KİLİTLİ] {lock_reason}")
        return

    # 2. Canlı Bülteni Çek
    matches = harvester.fetch_live_program()
    if not matches:
        print("[!] Maçkolik bülteni boş veya erişilemedi.")
        return

    print(f"[✓] Maçkolik üzerinden toplam {len(matches)} maç bülteni başarıyla çekildi.")

    # 3. Bugünden kalan saatlere göre sırala
    now = datetime.now()
    current_minutes = now.hour * 60 + now.minute

    upcoming_today = []
    night_tomorrow = []

    for m in matches:
        t_min = parse_match_time(m)
        if t_min >= current_minutes:
            upcoming_today.append((t_min, m))
        else:
            night_tomorrow.append((t_min, m))

    upcoming_today.sort(key=lambda x: x[0])
    night_tomorrow.sort(key=lambda x: x[0])

    # En yakın maçlardan başlayarak analiz et
    target_matches = [m for _, m in upcoming_today] + [m for _, m in night_tomorrow]
    print(f"[✓] Günün en yakın saatinden başlayarak analiz kuyruğu oluşturuldu ({len(target_matches)} maç).")

    # En yüksek değer (+EV) ve güven skoruna sahip maçları seç (En fazla 5 ideal kupon maçı)
    selected_bets = []
    analyzed_count = 0

    print("\n🔍 Karşılaşmalar Quant & AI Modelleriyle Taranıyor...")
    print("-" * 75)

    for m in target_matches:
        if len(selected_bets) >= 5:
            break

        analyzed_count += 1
        odds = m.get("oranlar", {})
        ms1 = odds.get("ms_1", 0.0)
        msx = odds.get("ms_x", 0.0)
        ms2 = odds.get("ms_2", 0.0)
        alt25 = odds.get("alt_25", 0.0)
        ust25 = odds.get("ust_25", 0.0)

        # Oran kontrolü
        if ms1 <= 1.0 or ms2 <= 1.0:
            continue

        match_name = f"{m.get('ev_sahibi')} vs {m.get('deplasman')}"
        lig = m.get("lig", "")
        saat = m.get("saat", "")

        # İstatistiksel Güç ve Ağırlıklandırma
        is_cup = "Kupa" in lig or "Cup" in lig
        is_dev = "Development" in lig or "U21" in match_name

        # Ev ve Deplasman özellikleri
        h_feat = {"kadro": 0.7 if ms1 < 1.9 else 0.5, "form": 0.65, "dinlenme": 0.8}
        a_feat = {"kadro": 0.7 if ms2 < 2.0 else 0.5, "form": 0.60, "dinlenme": 0.6, "seyahat": 0.6 if is_cup else 0.2}

        # Model Tahmini
        pred = learner.predict_match(h_feat, a_feat, odds)
        pick = pred["secilen_bahis"]
        pick_odds = pred["oran"]
        confidence = pred["guven_skoru"]

        calc_prob = pred["p_1"] if pick == "MS 1" else (pred["p_2"] if pick == "MS 2" else (pred["p_x"] if pick == "MS X" else 58.0))

        # Risk Guardian Onayı
        is_valid, validation_msg = guardian.validate_odds_risk_balance(pick_odds, calc_prob, pick)
        if not is_valid:
            continue

        # Quant Değerlendirmesi (+EV Alpha)
        ev_alpha = calculate_expected_value(calc_prob, pick_odds)
        if ev_alpha <= 0 and confidence < 75.0:
            continue

        # Dinamik Kelly Stake (Kasa güvenliği için %1 - %3 bandı)
        calculated_stake, _ = bankroll_mgr.calculate_kelly_stake(pick_odds, calc_prob / 100.0, fraction=0.25)
        # Minimum 100 TL, maksimum 400 TL güvenli sınır
        stake = max(100.0, min(350.0, calculated_stake if calculated_stake > 0 else 150.0))

        # SQLite'a PENDING olarak kaydet
        bet_id = bankroll_mgr.record_bet(
            match_name=f"[{saat}] {match_name} ({pick})",
            odds=pick_odds,
            probability=calc_prob / 100.0,
            stake=stake
        )

        if bet_id > 0:
            # Telemetriye kaydet
            guardian.log_telemetry(
                "OTONOM_BAHIS_ACILDI",
                {
                    "bet_id": bet_id,
                    "mac": match_name,
                    "saat": saat,
                    "lig": lig,
                    "secim": pick,
                    "oran": pick_odds,
                    "olasilik": calc_prob,
                    "ev_alpha": ev_alpha,
                    "yatirilan": stake
                },
                f"Quant Alpha: %{ev_alpha:.1f} | Güven: %{confidence:.1f} | Model Onayladı."
            )

            selected_bets.append({
                "bet_id": bet_id,
                "mac": match_name,
                "lig": lig,
                "saat": saat,
                "secim": pick,
                "oran": pick_odds,
                "olasilik": calc_prob,
                "ev_alpha": ev_alpha,
                "guven": confidence,
                "yatirilan": stake
            })

            print(f"[🎯 SEÇİLDİ #{len(selected_bets)}] {saat} | {match_name}")
            print(f"      👉 Tahmin: {pick} | Oran: {pick_odds} | Güven: %{confidence:.1f} | +EV: %{ev_alpha:.1f} | Yatırılan: {stake:.2f} TL")

    # Robot durumunu kaydet
    robot_state = {
        "aktif_bahisler": selected_bets,
        "son_guncelleme": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "toplam_secilen": len(selected_bets)
    }
    with open(ROBOT_STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(robot_state, f, ensure_ascii=False, indent=2)

    # HTML Dashboard güncelle
    try:
        html = generate_mackolik_dashboard_html()
        with open(project_root / "ui" / "mackolik_robot_dashboard.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("[✓] Web Dashboard güncellendi: ui/mackolik_robot_dashboard.html")
    except Exception as e:
        print(f"[!] Dashboard güncelleme uyarısı: {e}")

    print("\n" + "=" * 75)
    print(f"📊 OTONOM SEÇİM ÖZETİ: {len(selected_bets)} Maç İçin Bahis Açıldı")
    print(f"💰 Güncel Kalan Kasa: {bankroll_mgr.get_current_balance():,.2f} TL")
    print("=" * 75)

    return selected_bets


if __name__ == "__main__":
    run_autonomous_betting_session()
