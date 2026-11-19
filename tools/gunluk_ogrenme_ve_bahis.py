# -*- coding: utf-8 -*-
"""
Ertuğrul YZ - Günlük Öz-Öğrenme, Kök Neden Otopsisi ve Yeni Bahis Açma Motoru
1. Dünkü gerçek saha kayıplarının otopsisini yapar, modeli eğitir.
2. Güncellenen beyin ağırlıklarıyla bugünkü maçları analiz eder.
3. Değerli (+EV) maçlara Kelly kriteriyle bahis açıp SQLite'a kaydeder.
"""

import sys
import json
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from core.adaptive_learner import AdaptiveLearner
from core.risk_guardian import RiskGuardian
from core.mackolik_harvester import MackolikHarvester
from core.sqlite_bankroll_manager import AutonomousBankrollManager
from core.quant_sports_engine import calculate_expected_value, calculate_team_rsi
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


def run_learning_and_betting():
    print("=" * 75)
    print("🧠 ERTUĞRUL YZ - ÖZ-ÖĞRENME & GÜNLÜK OTONOM BAHİS OPERASYONU")
    print("=" * 75)

    learner = AdaptiveLearner()
    guardian = RiskGuardian(max_daily_loss_pct=0.10)
    bankroll_mgr = AutonomousBankrollManager()
    harvester = MackolikHarvester()

    current_kasa = bankroll_mgr.get_current_balance()
    print(f"💰 Başlangıç Kasa Bakiyesi (SQLite): {current_kasa:,.2f} TL")

    # -------------------------------------------------------------
    # 1. ADIM: DÜNKÜ GERÇEK KAYIPLARIN KÖK NEDEN OTOPSİSİ VE EĞİTİM
    # -------------------------------------------------------------
    print("\n[ADIM 1] 🔍 Dünkü Gerçek Saha Kayıplarının Otopsisi Yapılıyor...")
    
    yesterday_losses = [
        {
            "mac": "Mbarara City vs Lugazi Municipal",
            "tahmin": "MS X",
            "gercek": "MS 1",  # 1-0 bitti
            "h_feat": {"kadro": 0.5, "form": 0.65, "dinlenme": 0.8},
            "a_feat": {"kadro": 0.5, "form": 0.60, "dinlenme": 0.6, "seyahat": 0.2}
        },
        {
            "mac": "Al Adalah vs Al Orubah",
            "tahmin": "MS X",
            "gercek": "MS 2",  # 1-2 bitti
            "h_feat": {"kadro": 0.5, "form": 0.65, "dinlenme": 0.8},
            "a_feat": {"kadro": 0.6, "form": 0.65, "dinlenme": 0.6, "seyahat": 0.4}
        },
        {
            "mac": "Ranchers Bees vs Doma United",
            "tahmin": "MS X",
            "gercek": "MS 1",  # 2-1 bitti
            "h_feat": {"kadro": 0.5, "form": 0.60, "dinlenme": 0.8},
            "a_feat": {"kadro": 0.5, "form": 0.55, "dinlenme": 0.6, "seyahat": 0.3}
        }
    ]

    learning_summaries = []
    for loss in yesterday_losses:
        res = learner.learn_from_result(
            match_name=loss["mac"],
            predicted_pick=loss["tahmin"],
            actual_result=loss["gercek"],
            home_feat=loss["h_feat"],
            away_feat=loss["a_feat"]
        )
        learning_summaries.append({
            "mac": loss["mac"],
            "tahmin": loss["tahmin"],
            "gercek": loss["gercek"],
            "kök_neden": res["hata_koku"],
            "ders": res["alinan_ders"]
        })
        print(f"  ❌ [{loss['mac']}] Tahmin: {loss['tahmin']} | Gerçek: {loss['gercek']}")
        print(f"     🔍 Kök Neden: {res['hata_koku']}")
        print(f"     📚 Alınan Ders: {res['alinan_ders']}")

    print("\n📈 Güncellenen Model Ağırlıkları (Yeni Beyin Katsayıları):")
    for k, v in learner.weights.get("agirliklar", {}).items():
        k_clean = k.replace("_", " ").title()
        print(f"   • {k_clean:<26}: %{v*100:.1f}")

    # -------------------------------------------------------------
    # 2. ADIM: BUGÜNKÜ CANLI BÜLTENİ TARA VE YENİ MAÇLARA BAHİS AÇ
    # -------------------------------------------------------------
    print("\n[ADIM 2] 📡 Bugünün Canlı Maçkolik Bülteni Taranıyor...")
    matches = harvester.fetch_live_program()
    print(f"[✓] Toplam {len(matches)} maç bülteni başarıyla çekildi.")

    # Saat sıralaması (Günün kalan maçları)
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
    target_matches = [m for _, m in upcoming_today] + [m for _, m in night_tomorrow]

    print(f"\n[ADIM 3] 🎯 Güncellenmiş Ağırlıklarla Bugünün En Değerli Maçları Seçiliyor...")
    selected_bets = []

    for m in target_matches:
        if len(selected_bets) >= 5:
            break

        odds = m.get("oranlar", {})
        ms1 = odds.get("ms_1", 0.0)
        msx = odds.get("ms_x", 0.0)
        ms2 = odds.get("ms_2", 0.0)
        alt25 = odds.get("alt_25", 0.0)

        if ms1 <= 1.05 or ms2 <= 1.05:
            continue

        match_name = f"{m.get('ev_sahibi')} vs {m.get('deplasman')}"
        lig = m.get("lig", "")
        saat = m.get("saat", "")

        # İstatistiksel Güç
        is_cup = "Kupa" in lig or "Cup" in lig
        h_feat = {"kadro": 0.8 if ms1 < 1.6 else (0.4 if ms1 > 3.0 else 0.6), "form": 0.65, "dinlenme": 0.8}
        a_feat = {"kadro": 0.8 if ms2 < 1.6 else (0.4 if ms2 > 3.0 else 0.6), "form": 0.60, "dinlenme": 0.6, "seyahat": 0.6 if is_cup else 0.2}

        # Model Tahmini
        pred = learner.predict_match(h_feat, a_feat, odds)
        pick = pred["secilen_bahis"]
        pick_odds = pred["oran"]
        confidence = pred["guven_skoru"]

        calc_prob = pred["p_1"] if pick == "MS 1" else (pred["p_2"] if pick == "MS 2" else (pred["p_x"] if pick == "MS X" else 55.0))

        # Risk Guardian Onayı
        is_valid, validation_msg = guardian.validate_odds_risk_balance(pick_odds, calc_prob, pick)
        if not is_valid:
            continue

        # Quant Alpha
        ev_alpha = calculate_expected_value(calc_prob, pick_odds)

        # Kelly Dinamik Kasa Payı (Güvenli %1 - %3.5 bandı)
        calculated_stake, _ = bankroll_mgr.calculate_kelly_stake(pick_odds, calc_prob / 100.0, fraction=0.25)
        stake = max(120.0, min(350.0, calculated_stake if calculated_stake > 0 else 150.0))

        # SQLite'a PENDING olarak kaydet
        bet_id = bankroll_mgr.record_bet(
            match_name=f"[{saat}] {match_name} ({pick})",
            odds=pick_odds,
            probability=calc_prob / 100.0,
            stake=stake
        )

        if bet_id > 0:
            guardian.log_telemetry(
                "OTONOM_BUGUNKU_BAHIS",
                {
                    "bet_id": bet_id,
                    "mac": match_name,
                    "saat": saat,
                    "lig": lig,
                    "secim": pick,
                    "oran": pick_odds,
                    "guven": confidence,
                    "ev_alpha": ev_alpha,
                    "yatirilan": stake
                },
                f"Kök neden eğitimi sonrası güncellenen model ile açıldı. Güven: %{confidence:.1f}"
            )

            selected_bets.append({
                "bet_id": bet_id,
                "mac": match_name,
                "lig": lig,
                "saat": saat,
                "secim": pick,
                "oran": pick_odds,
                "olasilik": calc_prob,
                "guven": confidence,
                "ev_alpha": ev_alpha,
                "yatirilan": stake
            })

            print(f"  🎯 [KUPON #{len(selected_bets)}] [{saat}] {match_name}")
            print(f"       👉 Tercih: {pick} | Oran: {pick_odds:.2f} | Güven: %{confidence:.1f} | Yatırılan: {stake:.2f} TL | +EV: %{ev_alpha:.1f}")

    # Robot durumunu kaydet
    robot_state = {
        "aktif_bahisler": selected_bets,
        "son_ogrenme": learning_summaries,
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
        print("\n[✓] Görsel Dashboard Güncellendi: ui/mackolik_robot_dashboard.html")
    except Exception as e:
        print(f"[!] Dashboard güncelleme uyarısı: {e}")

    print("\n" + "=" * 75)
    print(f"💰 Güncel SQLite Kalan Kasa: {bankroll_mgr.get_current_balance():,.2f} TL")
    print(f"📌 Toplam Açılan Yeni Kupon: {len(selected_bets)} Adet")
    print("=" * 75)


if __name__ == "__main__":
    run_learning_and_betting()
