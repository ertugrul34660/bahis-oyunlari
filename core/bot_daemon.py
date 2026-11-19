# -*- coding: utf-8 -*-
"""
Ertuğrul YZ - Otonom Bahis ve Öz-Öğrenme Daemon Botu
5. Kat: AR-GE, 3D Simülasyon, Oyun & Spor Analiz Laboratuvarı

Görevler:
1. Her maçı analiz eder, sanal kasadan bahis oynar.
2. Sonuçları kontrol eder.
3. BİLEMEZSE: "Nerede kaybettik?" analizini yapar (Kök Neden Otopsisi).
4. Hatasından öğrenip model ağırlıklarını kalıcı olarak günceller.
"""

import sys
import time
from pathlib import Path
from typing import Dict, Any, List

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from core.adaptive_learner import AdaptiveLearner
from core.bankroll_manager import BankrollManager
from ui.dashboard_generator import generate_bot_dashboard_html

class AutonomousBettingBot:
    def __init__(self):
        self.learner = AdaptiveLearner()
        self.bankroll = BankrollManager()

    def process_match(self, match_info: Dict[str, Any], actual_result: str = None) -> Dict[str, Any]:
        """Bir maçı analiz eder, bahis yapar, varsa sonucunu işleyip öğrenir."""
        m_name = f"{match_info['ev_sahibi']} vs {match_info['deplasman']}"
        h_feat = match_info.get("ev_ozellikler", {"kadro": 0.5, "form": 0.5, "dinlenme": 0.7})
        a_feat = match_info.get("dep_ozellikler", {"kadro": 0.7, "form": 0.6, "dinlenme": 0.5, "seyahat": 0.4})
        odds = match_info.get("oranlar", {"ms_1": 2.5, "ms_x": 3.2, "ms_2": 2.2, "alt_25": 1.75})

        # 1. Tahmin ve Değerli Bahis Seçimi
        prediction = self.learner.predict_match(h_feat, a_feat, odds)
        pick = prediction["secilen_bahis"]
        odds_val = prediction["oran"]
        confidence = prediction["guven_skoru"]

        # 2. Sanal Kasadan Bahis Oyna
        bet = self.bankroll.place_bet(m_name, pick, odds_val, confidence)

        report = {
            "mac": m_name,
            "tahmin": pick,
            "oran": odds_val,
            "guven": confidence,
            "yatirilan_tutar": bet["yatirilan_tutar"],
            "olasiliklar": {
                "MS 1": prediction["p_1"],
                "MS X": prediction["p_x"],
                "MS 2": prediction["p_2"]
            }
        }

        # 3. Sonuç Belli İse Öğrenme Döngüsünü Çalıştır
        if actual_result:
            is_won = (pick == actual_result)
            settled_bet = self.bankroll.settle_bet(bet["bet_id"], is_won)
            learning_result = self.learner.learn_from_result(
                match_name=m_name,
                predicted_pick=pick,
                actual_result=actual_result,
                home_feat=h_feat,
                away_feat=a_feat
            )
            report["sonuc"] = "KAZANDI" if is_won else "KAYBETTİ"
            report["kazanc_kayip"] = settled_bet.get("kazanc", 0.0)
            report["hata_koku"] = learning_result["hata_koku"]
            report["alinan_ders"] = learning_result["alinan_ders"]
            report["yeni_agirliklar"] = learning_result["guncel_agirliklar"]

        # 4. Görsel Gösterge Panelini Güncelle
        self._update_dashboard()

        return report

    def _update_dashboard(self):
        try:
            html = generate_bot_dashboard_html()
            dash_path = project_root / "ui" / "bot_dashboard.html"
            with open(dash_path, "w", encoding="utf-8") as f:
                f.write(html)
        except Exception as e:
            print(f"[!] Dashboard güncellenirken hata: {e}")

    def run_simulation_cycle(self, test_matches: List[Dict[str, Any]]):
        """Örnek maçlar üzerinden botun öğrenme yeteneğini test eden simülasyon."""
        results = []
        for m in test_matches:
            res = self.process_match(m, actual_result=m.get("gercek_sonuc"))
            results.append(res)
        return results
